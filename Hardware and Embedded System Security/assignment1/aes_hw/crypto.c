#include "crypto.h"

// This is included for the AES driver
#include <stdio.h>
#include <aes256.h>
#include <assert.h>

#include "inc/hw_regaccess.h"
#include "inc/hw_memmap.h"

//*****************************************************************************
//
// Locations written for use in optimised code solution
//
//*****************************************************************************	
#define SELECT_KEY_TYPE													 0xFFF9
#define BASE_KEY_LOC													 0x09C6
#define BASE_STAT_LOC													 0x09C4
#define BASE_IN_LOC														 0x09C8
#define BASE_OUT_LOC													 0x09CA

//The original function was uint8_t AES256_setCipherKey(uint16_t baseAddress, const uint8_t * cipherKey,uint16_t keyLength)
//Removed switch() statements for choosing different varieties of key
uint8_t Opt_setCipherKey(const uint8_t * cipherKey,uint16_t keyLength)
{
    uint8_t i;
    uint16_t sCipherKey;
	
    //HWREG16(baseAddress + OFS_AESACTL0) &= (~(AESKL_1 + AESKL_2));
	//HWREG16(baseAddress + 0x0000) &= (~(0x0004 + 0x0008)); 
	//HWREG16(baseAddress) &= (0xFFF9);
	HWREG16(AES256_BASE) &= (SELECT_KEY_TYPE); // Reduced down by hardcoding several operations.
	
	//HWREG16(baseAddress + OFS_AESACTL0) |= AESKL__128;
    //HWREG16(baseAddress + 0) |= 0; // Removed this line; an OR operation of all zero bits has no effect on the original value.
	
    //keyLength = keyLength / 8; //Better to just pass through the keylength / 8 to avoid this extra operation

    for(i = 0; i < keyLength; i = i + 2)
    {
        sCipherKey = (uint16_t)(cipherKey[i]);
        sCipherKey = sCipherKey | ((uint16_t)(cipherKey[i + 1]) << 8);
        //HWREG16(baseAddress + OFS_AESAKEY) = sCipherKey;
		HWREG16(BASE_KEY_LOC) = sCipherKey;    // looked up both locations and hardcoded the addition
    }

    // Wait until key is written
	// while(0x00 == (HWREG16(baseAddress + OFS_AESASTAT) & AESKEYWR))
	//										0x0004			0x0002
    while(0x00 == (HWREG16(BASE_STAT_LOC) & AESKEYWR))		// Harcoded addition for address
    {
        ;
    }
    return(STATUS_SUCCESS);
}

// The original function was void AES256_encryptData(uint16_t baseAddress, const uint8_t * data, uint8_t * encryptedData)
// Removed switch() statements for choosing different types of encryption
void Opt_encryptData(const uint8_t * data, uint8_t * encryptedData)
{
    uint8_t i;
    uint16_t tempData = 0;
    uint16_t tempVariable = 0;

    // Set module to encrypt mode
	//HWREG16(baseAddress + OFS_AESACTL0) &= ~AESOP_3;
    //HWREG16(AES256_BASE) &= 0xFFFC;
	HWREG16(AES256_BASE) &= ~AESOP_3;  					// Hardcoding the negation operation yielded no performance benefit
	

    // Write data to encrypt to module
    for(i = 0; i < 16; i = i + 2)
    {
        tempVariable = (uint16_t)(data[i]);
        tempVariable = tempVariable | ((uint16_t)(data[i + 1]) << 8);
        //HWREG16(baseAddress + OFS_AESADIN) = tempVariable;
		HWREG16(BASE_IN_LOC) = tempVariable;
    }

    // Key that is already written shall be used
    // Encryption is initialized by setting AESKEYWR to 1
    //HWREG16(baseAddress + OFS_AESASTAT) |= AESKEYWR;
	//			0x09C0			0X0004		  0X0002
	HWREG16(BASE_STAT_LOC) |= AESKEYWR;						// addition hardcoded in #define
	
    // Wait unit finished ~167 MCLK
    while(AESBUSY == (HWREG16(BASE_STAT_LOC) & AESBUSY))
    {
        ;
    }

    // Write encrypted data back to variable
    for(i = 0; i < 16; i = i + 2)
    {
		//tempData = HWREG16(baseAddress + OFS_AESADOUT)
        tempData = HWREG16(BASE_OUT_LOC);
        *(encryptedData + i) = (uint8_t)tempData;
        *(encryptedData + i + 1) = (uint8_t)(tempData >> 8);
    }
}




void crypto_func(uint8_t pt[CRYPTO_IN_SIZE], uint8_t key[CRYPTO_KEY_SIZE])
{
	
	// Header definitions for reference when optimising code
	//uint8_t AES256_setCipherKey(uint16_t baseAddress,const uint8_t *cipherKey,uint16_t keyLength);
	//void AES256_encryptData(uint16_t baseAddress,const uint8_t *data,uint8_t *encryptedData);
	//void AES256_decryptData(uint16_t baseAddress,const uint8_t *data,uint8_t *decryptedData);
	//uint8_t AES256_setDecipherKey(uint16_t baseAddress,const uint8_t *cipherKey,uint16_t keyLength);
	//AES256_setCipherKey(AES256_BASE, key, 16);
	//AES256_encryptData(AES256_BASE, pt, pt);
	
	// Multi-path functions in the driver added clock cycles. By manually selecting the path and removing branches, clock cycles are saved.
	// Our functions implement the driver's code with a single path.
	Opt_setCipherKey(key, 16); //sent in as 128 / 8
	Opt_encryptData(pt, pt);
}



