#include "crypto.h"
#include <stdio.h>

/* Using destructive iteration instead of this function - seems to save a lot of cycles.
static uint8_t getbit(uint8_t src, uint8_t pos)
{
	uint8_t bit = src >> pos;	    // shift the bit we want -pos- places right, which should put it at position 0.
	return bit & 0x01;				// mask with 00000001 so we only get the value of the desired bit.
}
*/

static void setbit_16(bs_reg_t *src, uint8_t pos)
{
	bs_reg_t bit = 1 << pos; // move 1 -pos- places right
	*src = *src | bit;      // OR operation; if it was already 1, it will remain so. If it was 0, it will now be set.
}

static void setbit_8(uint8_t *src, uint8_t pos)
{
	uint8_t bit = 1 << pos; // move 1 -pos- places right
	*src = *src | bit;      // OR operation; if it was already 1, it will remain so. If it was 0, it will now be set.
}

/**
 * Bring normal buffer into bitsliced form
 * @param pt Input: state_bs in normal form
 * @param state_bs Output: Bitsliced state
 */
static void enslice(const uint8_t pt[CRYPTO_IN_SIZE * BITSLICE_WIDTH], bs_reg_t state_bs[CRYPTO_IN_SIZE_BIT])
{
	// with CRYPTO_IN_SIZE  8 and BITSLICE_WIDTH 16, pt has length 8 bytes * 8 (as bits) * 16 = 1024 bits.
	// bs_reg_t is uint16_t; with CRYPTO_IN_SIZE_BIT (CRYPTO_IN_SIZE * 8) and CRYPTO_IN_SIZE  8, it is 16 * 8 * 8 = 1024 bits, 64 elements of 16 bits; all matches up.
	
	// Each element of state_bs is 16 bits long; in the first element, each bit comes from the first bit from each block, and so on.
	// pt has 8*16 = 128 elements, each consisting of 8 bits, = 1024 bits
	// one block is eight consecutive elements, 8*8 = 64 bits in length

	// bs has 64 elements of 16 bits; each element contains the bits for one position of a block. Element 0 contains all the 0-position bits for each of the 16 blocks.
	// Each block's bits [64] are spread across one position within these 16 bit elements; block 4 is spread through all the uint16_t in bs, at bs[x][4]. 

	/* for example,
	pt[0][0] goes in bs[0][0]
	pt[0][1] goes in bs[1][0]
	pt[0][2] goes in bs[2][0]

	pt[1][0] goes in bs[0][1]
	pt[1][3] goes in bs[3][0]

	and,
	bitsliced block 0
	pt[0][0], pt[1][0],pt[2][0]

	bitsliced block 1
	pt[0][1], pt[1][1], pt[2][1]
	*/
	
	uint8_t which_block;		// block counter, i
	uint8_t which_byte;			// byte counter,  j
	uint8_t which_bit;			// bit counter,   k


	for(which_block = 0; which_block < BITSLICE_WIDTH; which_block++) 		// there are 16 [BITSLICE_WIDTH] blocks
	{
		for(which_byte = 0; which_byte < CRYPTO_IN_SIZE; which_byte++) 		// there are eight [CRYPTO_IN_SIZE] bytes in a block [8*8 = 64-bit plaintexts]
		{
			uint8_t this_byte = pt[which_block * 8 + which_byte];			// the position in the pt for this byte within block i*8;
																			// so this the byte in the pt who's bits we will examine next
			
			uint8_t bits_done = which_byte * 8;								// the index into state_bs we're using is the bit position within our 8x8 blocks, 0-63
																			// this is the number of bits we've already done in previous bytes; 
																			// calculate it here so it's only done once per byte.
			
			/*
			if(this_byte & 0x1) { setbit_16(&state_bs[bits_done], which_block); }
			if((this_byte >>= 1) & 0x1) { setbit_16(&state_bs[bits_done+1], which_block); }
			if((this_byte >>= 1) & 0x1) { setbit_16(&state_bs[bits_done+2], which_block); }
			if((this_byte >>= 1) & 0x1) { setbit_16(&state_bs[bits_done+3], which_block); }
			if((this_byte >>= 1) & 0x1) { setbit_16(&state_bs[bits_done+4], which_block); }
			if((this_byte >>= 1) & 0x1) { setbit_16(&state_bs[bits_done+5], which_block); }
			if((this_byte >>= 1) & 0x1) { setbit_16(&state_bs[bits_done+6], which_block); }
			if((this_byte >>= 1) & 0x1) { setbit_16(&state_bs[bits_done+7], which_block); }
			*/
			
			// Unrolling this loop had zero effect on execution cycles
			for(which_bit = 0; which_bit < 8; which_bit++)      			// iterate over the 8 bits of this byte; starting from bits_done didn't improve performance
			{
				uint8_t bit = this_byte & 0x1;								// checking this outside the if is faster than making it inline
				if(bit)														// Check lsb [which is initially the 0th bit]
				{
					setbit_16(&state_bs[bits_done + which_bit], which_block);    // the bit position within a block is the number of bits done previously + bits in this byte
																				 // Doing this without the function call with various other tweaks is consistently slower
																				 // than calling setbit_16; clearly some C magic is at work.
				}
				// else clear bit; not necessary as state_bs has been zeroed

				this_byte = this_byte >> 1; 								// shift the next bit we'll want into lsb position
																			// doing this for each iteration over the byte should be cheaper than getbit() for each bit
																			// as that'll end up doing multiple shifts for each bit beyond the first.
																			// We can destructively iterate over this_byte as it's just a copy.
																			// Wastes some space, saves a fair amount of time.
				
				// Unfortunately, the method below isn't quicker [which is odd - it feels like it should be], but was fun.
				// We can build the state by setting the top bit and shifting down
				// Every bit in every state element is checked, so they'll all be shifted to the right position eventually. 
				/*				
				uint8_t bit = this_byte & 0x1;
				uint8_t index = bits_done + which_bit;
				if(bit)
				{
					state_bs[index] = (state_bs[index] >> 1) | 0x8000;	// shift left one and set top bit
				}
				else
				{
					state_bs[index] = (state_bs[index] >> 1);			// shift left one and leave the new MSB as 0
				}
				
				this_byte = this_byte >> 1;	// destructively iterate */
			}
		}
	}
}

/**
 * Bring bitsliced buffer into normal form
 * @param state_bs Input: Bitsliced state
 * @param pt Output: state_bs in normal form
 */
static void unslice(const bs_reg_t state_bs[CRYPTO_IN_SIZE_BIT], uint8_t pt[CRYPTO_IN_SIZE * BITSLICE_WIDTH])
{
	// Recall that the sliced state_bs has all 0th bits in [0], all 1st bits in [1]; 
	// There are 16 blocks, so each element is of size 16 bits.
	// We are working on blocks of 8 bytes, so there are 64 bit positions to keep track of; thus state_bs has 8 bytes * 8 bits = 64 elements.
	// We need to put these back into a linear format within pt, which has elements of size 8 bits. 
	// Each block is eight bytes (made up of 8 elements), and we are working with 16 blocks, so pt has 8 * 16 elements.
	
	uint8_t bit_position; // our counter for bits, up to the 64th bit.
	
	// To unslice, we can iterate over the elements in our bitsliced array; recall each element holds 16 bits, 
	// each of which belongs to a bit in the same position in all our plaintexts.
	
	// Once a bit is recovered from state_bs, it can be placed in the correct bit in the correct byte of the correct block of the plaintext.
	
	for(bit_position = 0; bit_position < CRYPTO_IN_SIZE_BIT; bit_position++)
	{
		bs_reg_t current_word = state_bs[bit_position]; // take a copy of the word that contains all the bits that come from bit_position in the plaintexts
														// we can destructively iterate through this - again, quicker than getbit()
		
														// we now have to spread these bits throughout pt, with 64-bit spacing (the block size)
														// eg. the first bit in current_word is the first bit of the first block in pt; 
														// the second bit in current_word is the first bit of the second block in pt; etc
		
		// Where does this bit come from in all the plaintexts?
		uint8_t which_byte = bit_position / 8;
		uint8_t which_bit = bit_position % 8;
		
		uint8_t which_block;		// a counter for which block in the pt we are accessing
		
		for(which_block = 0; which_block < 16; which_block++)
		{
			//uint8_t this_bit = current_word & 0x01;
			
			// Let's assume our output array has been zeroed by a kindly calling function.
			// This is quicker than us selectively zeroing bits as it can be done bytewise, no shifts required.
			// It means we don't need to worry if it's a zero bit - saves a bit of time. (!)
			if(current_word & 0x01)
			{
				setbit_8(&pt[(which_block * 8) + which_byte], which_bit);
			}
			// else { } // No need for this!

			current_word = current_word >> 1;	// destructive iteration as we don't need the bitsliced state any more.
	 	}
	}	
}

/**
 * Perform next key schedule step
 * @param key Key register to be updated
 * @param r Round counter
 * @warning For correct function, has to be called with incremented r each time
 * @note You are free to change or optimize this function
 */
static void update_round_key(uint8_t key[CRYPTO_KEY_SIZE], const uint8_t r)
{	
	const uint8_t sbox[16] = {
		0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2,
	};

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

static void expand_key(uint8_t roundkey[CRYPTO_IN_SIZE], bs_reg_t expanded_key[CRYPTO_IN_SIZE_BIT])
{
	// roundkey is 64 bits in size (not CRYPTO_KEY_SIZE);
	// it contains the round key for an entire block. roundkey[0] is the first 8 bits, roundkey[1] is the next 8 etc
	// if we treat this as a 64-bit value, we just need to expand each single bit to fill an entire 16-bit bs_reg_t, for xoring.
	
	uint8_t i; // byte
	uint8_t j; // bit
	for(i = 0; i < 8; i++)				// Iterate over elements in key [= bytes]
	{
		uint8_t byte = roundkey[i];		// Make a copy we can destructively iterate over
		uint8_t bits_done = i * 8;      // No sense calculating this eight times in the bit loop
		
		for(j = 0; j < 8; j++)	        // Iterate over bits in byte
		{
			// First, mask everything except LSB in our byte - & 0x1.
			// Cast, then expand the bit (1 or 0) to fill the entire bs_reg_t of size 16 bits.
			// We can cheat to do this by multiplying -bit- by -1; a 1 bit negated becomes -1, which is 0xFFFF (all 1s). A zero bit reamins all zeros.
			// Much quicker than using something like set_bit, or even an if. 
			expanded_key[bits_done + j] = - ((bs_reg_t) (byte & 0x1)); 
		
			// Then destructively iterate over our byte - saves those slow calls to getbit
			byte = byte >> 1;
		}
	}	
}

// We only use this in the very final round - it's merged into addkey_sbox_pbox_layer otherwise
static void add_round_key(bs_reg_t expanded_round_key[CRYPTO_IN_SIZE_BIT], bs_reg_t state[CRYPTO_IN_SIZE_BIT])
{
	uint8_t i;
	// Because the key is expanded, we can XOR straight through all elements in it and the bitsliced state.
	for(i = 0; i < CRYPTO_IN_SIZE_BIT; i++)
	{
		state[i] ^= expanded_round_key[i];
	}
}

static void addkey_sbox_pbox_layer(bs_reg_t state_bs[CRYPTO_IN_SIZE_BIT], bs_reg_t state_bs_out[CRYPTO_IN_SIZE_BIT], bs_reg_t expanded_round_key[CRYPTO_IN_SIZE_BIT])
{
	// The Gestalt Function
	// We need to represent the sbox lookup table used in the reference implementation as a set of Boolean functions
	// The boolean functions here were calculated using the butterfly method into ADF form.
	
	// the pbox operation cannot be done in place - we require a new place to put our output 
	// Thankfully a thoughtful calling function has given us a pointer to a suitable array
	// in the permutation, element i is moved to position i/4 + (i % 4) * 16. 
	
	// We may as well also XOR in our expanded round key here - saves a bit of looping.
	
	uint8_t i;
	
	for(i = 0; i < 16; i++) 		// 16 = 64 / 4; we apply the sboxes to 4-bit chunks, so state[0-3] will go in, then [4-7], etc.
	{
		bs_reg_t zeroth_bit = state_bs[i*4] ^ expanded_round_key[i*4]; 			 // All the "zeroth bits" for this sbox are in the first element
		bs_reg_t first_bit = state_bs[i*4 + 1] ^ expanded_round_key[i*4 +1];     // All the "first bits", etc
		bs_reg_t second_bit = state_bs[i*4 + 2] ^ expanded_round_key[i*4 +2];	 // We can XOR in the expanded round key here too.
		bs_reg_t third_bit = state_bs[i*4 + 3] ^ expanded_round_key[i*4 +3];
		// sadly pre-calculating a lot of the common calculations here didn't speed things up, eg. j = i*4 didn't help.

		// The next step uses our calculated Boolean functions to simulate the lookup tables used in the reference implementation
		// These have been factorised to reduce the number of operations that need to be performed. 
		// @TODO: This could be improved[?] by introducing other logical operations that can replace sets of XOR and AND, perhaps
		// @TODO: Can we simplify some of the pbox indexes as we have for the final one?
		
		// Where we had a 1 in our boolean functions, use 0xFFFF = 1111 1111 1111 1111.
		// @DEV Tested with zeroes - this order of boxes seems to yield 0000 >> cccc which is right
				
		// Note that we perform the permutation layer right here - the calculation takes place in the index of state_bs_out.
		// Using NOT instead of XOR 0xFFFF is very slightly slower for some reason.
		state_bs_out[ ((i*4+3) / 4) + ((i*4+3) % 4) * 16 ] = 0xFFFF ^ zeroth_bit ^ (first_bit & (0xFFFF ^ (second_bit & (0xFFFF ^ zeroth_bit)))) ^ (third_bit & (0xFFFF ^ (zeroth_bit & (first_bit ^ second_bit))));
		state_bs_out[ ((i*4+2) / 4) + ((i*4+2) % 4) * 16 ] = 0xFFFF ^ (zeroth_bit & first_bit) ^ second_bit ^ (third_bit & (0xFFFF ^ first_bit ^ (zeroth_bit & (0xFFFF ^ first_bit ^ second_bit))));
		state_bs_out[ ((i*4+1) / 4) + ((i*4+1) % 4) * 16 ] = (first_bit & (0xFFFF ^ (second_bit & zeroth_bit))) ^ (third_bit & (0xFFFF ^ ((0xFFFF ^ zeroth_bit) & (first_bit ^ second_bit))));
		
		/*		state_bs_out[ ((i*4+3) / 4) + ((i*4+3) % 4) * 16 ] = 0xFFFF ^ zeroth_bit ^ (first_bit & (0xFFFF ^ (second_bit & (0xFFFF ^ zeroth_bit)))) ^ (third_bit & (0xFFFF ^ (zeroth_bit & (first_bit ^ second_bit))));
		state_bs_out[ ((i*4+2) / 4) + ((i*4+2) % 4) * 16 ] = 0xFFFF ^ (zeroth_bit & first_bit) ^ second_bit ^ (third_bit & (0xFFFF ^ first_bit ^ (zeroth_bit & (0xFFFF ^ first_bit ^ second_bit))));
		state_bs_out[ ((i*4+1) / 4) + ((i*4+1) % 4) * 16 ] = (first_bit & (0xFFFF ^ (second_bit & zeroth_bit))) ^ (third_bit & (0xFFFF ^ ((0xFFFF ^ zeroth_bit) & (first_bit ^ second_bit))));*/
		
		// (i*4 / 4) + (i*4 %4) * 16 cancels out to just i! This works out as a tiny bit faster.
		state_bs_out[ i ] = zeroth_bit ^ second_bit ^ (first_bit & second_bit) ^ third_bit;		
	}	
}

void crypto_func(uint8_t pt[CRYPTO_IN_SIZE * BITSLICE_WIDTH], uint8_t key[CRYPTO_KEY_SIZE])
{
	// State buffer and additional backbuffer of same size
	// It's cheaper to zero the state buffer than to include a clearbit function
	// @TODO inexplicably it doesn't matter if our backstate isn't zeroed? Mysterious, but speedy.
	bs_reg_t state[CRYPTO_IN_SIZE_BIT] = {0};
	bs_reg_t state_back[CRYPTO_IN_SIZE_BIT];
	
	// We use the backbuffer and flip between them - this saves us iterating and copying the state back and forth
	// when we use the pbox layer, which cannot be done in place.
	bs_reg_t *currentstate = state;
	bs_reg_t *backstate = state_back;
	
	// Store the expanded key here
	// we don't need to zero it; it gets fully overwritten as we go.
	bs_reg_t expanded_key[CRYPTO_IN_SIZE_BIT];
	
	uint8_t i;	// counter
	
	// Bring into bitslicing form
	enslice(pt, currentstate);
	
	// PRESENT has 31 rounds plus an extra key XOR at the end.
	for(i = 1; i <= 31; i++)
	{
		// It is necessary to expand the key - each bit should be expanded to 16 identical bits.
		// This allows us to XOR each word of our bitsliced state with the key as a single operation - computationally efficient.
		// Expand the key. It's +2 because we only use the top 64 bits, as described in the template.
		expand_key(key +2, expanded_key);

		// Our boolean logic that simulates the lookup tables works its magic here
		// our pbox layer fits in nicely at the end of the sboxes, so we can merge the two layers into one function - less looping.
		// the permutation, which was so expensive in the reference implementation, is bytewise here instead of bitwise - much nicer.
		// We can also XOR our expanded key directly into the bitsliced state.
		addkey_sbox_pbox_layer(currentstate, backstate, expanded_key);
					
		// flip our states to use the permuted one for the next round
		bs_reg_t *tmp = backstate;
		backstate = currentstate;
		currentstate = tmp;
		
		// set the new backstate to zeroes - this helps us avoid clearbit, which is expensive.
		//memset(backstate, 0, CRYPTO_IN_SIZE_BIT);
		
		update_round_key(key, i);
		
	}	
	
	// final key addition
	expand_key(key +2, expanded_key);	
	add_round_key(expanded_key, currentstate);
		
	// Convert back to normal form
	// set the old plaintext to zeroes
	memset(pt, 0, CRYPTO_IN_SIZE * BITSLICE_WIDTH);
	unslice(currentstate, pt);
	
}