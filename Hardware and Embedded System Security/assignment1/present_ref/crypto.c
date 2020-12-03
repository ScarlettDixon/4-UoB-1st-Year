 v#include "crypto.h"

static uint8_t getbit(uint8_t src, uint8_t pos)
{
	uint8_t bit = src >> pos;	    // shift the bit we want -pos- places right, which should put it at position 0.
	return bit & 0x01;				// mask with 00000001 so we only get the value of the desired bit.
}

static void setbit(uint8_t *src, uint8_t pos)
{
	uint8_t bit = 1 << pos; // move 1 -pos- places right
	*src = *src | bit;      // OR operation; if it was already 1, it will remain so. If it was 0, it will now be set.
}


/*static void clearbit(uint8_t *src, uint8_t pos)
{
	uint8_t bit = 1 << pos; // move 1 -pos- places right
	bit = ~bit;				// invert bit
	*src = *src & bit;	    // AND mask will copy *src but leave the bit at -pos- unset.
}

static void copybit(uint8_t *src, uint8_t pos, uint8_t val)
{
	// is this cheaper than using IF to check if a bit is 0 or 1? We call setbit() as part of the process.
	
	// First remove the bit to be set or cleared from src
	clearbit(src, pos);
	
	uint8_t bit_to_set = val << pos;			// val in -pos-th position; if val is 0, this is all zero.
	*src = *src | bit_to_set;          			// if val was 0, we cleared the same bit in src, so remains zero. If val was 1, 0 OR 1 = 1, so bit is set.
}*/


static void add_round_key(uint8_t pt[CRYPTO_IN_SIZE], uint8_t roundkey[CRYPTO_IN_SIZE])
{
	uint8_t i; // declare counter
	for (i = 0; i < 8; i++) // Loop over the state
	{
		pt[i] = pt[i] ^ roundkey[i];  // XOR state with roundkey and place the result into the state.
	}
}

static const uint8_t sbox[16] = {
	0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2,
};

static void sbox_layer(uint8_t s[CRYPTO_IN_SIZE])
{
	// We need to take each byte of the state and split it into the upper and lower 4 bits.
	// Each 4 bit value is used as an index into sbox[16].
	// The output goes back into the state.
	
	uint8_t i; // declare counter
	for(i = 0; i < 8; i++) // iterate over state
	{
		uint8_t lower = s[i] & 0x0F;  // extract lower 4 bits (& with mask 00001111)
		uint8_t upper = s[i] >> 4;    // extract upper 4 bits (shift right 4 positions; the left is padded with zeroes automatically so no need to mask)
		
		lower = sbox[lower];          // sbox of index lower -> lower
		upper = sbox[upper] << 4;     // sbox of index upper left, shifted to most significant 4 bits -> upper
		
		s[i] = lower | upper;		  // lower -> least significant 4 bits, upper -> most significant 4 bits.
	}
}

static void pbox_layer(uint8_t s[CRYPTO_IN_SIZE])
{
	// For given bit at position i, the new position is i/4 + 16(i mod 4)
	
	uint8_t i; // declare counter
	uint8_t out[CRYPTO_IN_SIZE] = {0}; // this can't be done in-place as permutations would overwrite bits we later need.
	                             // the output of our permutation must therefore go somewhere new; let's put it here.
	
	for(i = 0; i < 64; i++)
	{
		uint8_t bit = getbit(s[i/8], i % 8); // get the i%8'th bit from the i/8'th byte (eg. bit 45 would be i/8 = 5th byte, i%8 = 5th bit
		uint8_t position = (i/4) + (16 * (i % 4)); 	// calculate where the bit we've just got needs to go.
		
		// see if setbitbyvalue() is faster than setbit() within an if
		/* 
		uint8_t byte = position/8;
		setbitbyvalue(&out[byte], position % 8, bit);
		*/
		
		// because out is zeroed, if this bit is zero, we don't need to do anything.
		if(bit)
		{
			uint8_t byte = position/8;
			setbit(&out[byte], position % 8);      // set that bit to 1
		}

	}
	
	for(i = 0; i < 8; i++)
	{
		s[i]=out[i];
	}
	//s = out;	// our old state is replaced by the new state
}

static void update_round_key(uint8_t key[CRYPTO_KEY_SIZE], const uint8_t r)
{
	uint8_t tmp = 0;
	const uint8_t tmp2 = key[2];
	const uint8_t tmp1 = key[1];
	const uint8_t tmp0 = key[0];
	
	// rotate right by 19 bit
	key[0] = key[2] >> 3 | key[3] << 5;
	key[1] = key[3] >> 3 | key[4] << 5;
	key[2] = key[4] >> 3 | key[5] << 5;
	key[3] = key[5] >> 3 | key[6] << 5;
	key[4] = key[6] >> 3 | key[7] << 5;
	key[5] = key[7] >> 3 | key[8] << 5;
	key[6] = key[8] >> 3 | key[9] << 5;
	key[7] = key[9] >> 3 | tmp0 << 5;
	key[8] = tmp0 >> 3   | tmp1 << 5;
	key[9] = tmp1 >> 3   | tmp2 << 5;
	
	// perform sbox lookup on MSbits
	tmp = sbox[key[9] >> 4];
	key[9] &= 0x0F;
	key[9] |= tmp << 4;
	
	// XOR round counter k19 ... k15
	key[1] ^= r << 7;
	key[2] ^= r >> 1;
}



void crypto_func(uint8_t pt[CRYPTO_IN_SIZE], uint8_t key[CRYPTO_KEY_SIZE])
{
	uint8_t i = 0;
	
	for(i = 1; i <= 31; i++)
	{
		// Note +2 offset on key since output of keyschedule are upper 8 byte
		add_round_key(pt, key + 2);
		sbox_layer(pt);
		pbox_layer(pt);
		update_round_key(key, i);
	}
	
	// Note +2 offset on key since output of keyschedule are upper 8 byte
	add_round_key(pt, key + 2);
}