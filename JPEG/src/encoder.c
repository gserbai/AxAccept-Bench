/*
 * encoder.c
 * 
 * Created on: Sep 9, 2013
 * 			Author: Amir Yazdanbakhsh <a.yazdanbakhsh@gatech.edu>
 */

#include "datatype.h"
#include "jpegconfig.h"
#include "prototype.h"
    #include<stdbool.h>
#include "rgbimage.h"
#include <time.h>


UINT8	Lqt [BLOCK_SIZE];
UINT8	Cqt [BLOCK_SIZE];
UINT16	ILqt [BLOCK_SIZE];
UINT16	ICqt [BLOCK_SIZE];

INT16	Y1 [BLOCK_SIZE];
INT16	Y2 [BLOCK_SIZE];
INT16	Y3 [BLOCK_SIZE];
INT16	Y4 [BLOCK_SIZE];
INT16	CB [BLOCK_SIZE];
INT16	CR [BLOCK_SIZE];
INT16	Temp [BLOCK_SIZE];
UINT32 lcode = 0;
UINT16 bitindex = 0;

INT16 global_ldc1;
INT16 global_ldc2;
INT16 global_ldc3;



UINT8* encodeImage(
	RgbImage* srcImage,
	UINT8 *outputBuffer,
	UINT32 qualityFactor,
	UINT32 imageFormat
) {
	

	global_ldc1 = 0;
	global_ldc2 = 0;
	global_ldc3 = 0;




	/** Quantization Table Initialization */
	initQuantizationTables(qualityFactor);

	srand(time(NULL));


	UINT16 i, j;
	/* Writing Marker Data */
	outputBuffer = writeMarkers(outputBuffer, imageFormat, srcImage->w, srcImage->h);
	
	if (imageFormat == GRAY) {
		// Modo escala de cinza: processa apenas luminância
		for (i = 0; i < srcImage->h; i += 8) {
			for (j = 0; j < srcImage->w; j += 8) {
				readMcuFromRgbImage(srcImage, j, i, Y1);
				outputBuffer = encodeMcu(1, outputBuffer, ILqt);
			}
		}
	} else {
		// Modo RGB: processa Y, Cb e Cr com downsampling 4:2:0
		for (i = 0; i < srcImage->h; i += 16) {
			for (j = 0; j < srcImage->w; j += 16) {
				// Processa 4 blocos Y (2x2)
				readYBlockFromRgbImage(srcImage, j, i, Y1);
				outputBuffer = encodeMcu(1, outputBuffer, ILqt);
				
				readYBlockFromRgbImage(srcImage, j + 8, i, Y2);
				outputBuffer = encodeMcu(1, outputBuffer, ILqt);
				
				readYBlockFromRgbImage(srcImage, j, i + 8, Y3);
				outputBuffer = encodeMcu(1, outputBuffer, ILqt);
				
				readYBlockFromRgbImage(srcImage, j + 8, i + 8, Y4);
				outputBuffer = encodeMcu(1, outputBuffer, ILqt);
				
				// Processa 1 bloco Cb (downsampled)
				readCbBlockFromRgbImage(srcImage, j, i, CB);
				outputBuffer = encodeMcu(2, outputBuffer, ICqt);
				
				// Processa 1 bloco Cr (downsampled)
				readCrBlockFromRgbImage(srcImage, j, i, CR);
				outputBuffer = encodeMcu(3, outputBuffer, ICqt);
			}
		}
	}

	/* Close Routine */
	closeBitstream(outputBuffer);

	return outputBuffer;
}

UINT8* encodeMcu(
	UINT32 componentId,
	UINT8 *outputBuffer,
	UINT16 *quantTable
) {
	INT16 *sourceBuffer;
	
	// Seleciona o buffer de dados correto baseado no componente
	switch(componentId) {
		case 1: sourceBuffer = Y1; break;
		case 2: sourceBuffer = Y2; break;
		case 3: sourceBuffer = Y3; break;
		case 4: sourceBuffer = Y4; break;
		case 5: sourceBuffer = CB; break;
		case 6: sourceBuffer = CR; break;
		default: sourceBuffer = Y1; break;
	}
	
	// Copia o buffer para Y1 para processar
	for (int k = 0; k < BLOCK_SIZE; k++) {
		Y1[k] = sourceBuffer[k];
	}
	
	levelShift(Y1);

	double dataIn [BLOCK_SIZE];
	double dataOut[BLOCK_SIZE];

	for (int i = 0; i < BLOCK_SIZE; ++i)
	{
		dataIn[i] = Y1[i] / 256.;
	}

	bool isNN = true;
		
	// #pragma parrot(input, "jpeg", [64]dataIn) // Removido
	
	dct(Y1);
	quantization(Y1, quantTable);

	for (int i = 0; i < BLOCK_SIZE; ++i)
	{
		dataOut[i] = Temp[i] / 256.;
	}
	
	// isNN = false; 

	// #pragma parrot(output, "jpeg", [64]<-0.9; 0.9>dataOut) // Removido

	for(int i = 0; i < BLOCK_SIZE; ++i)
	{
		Temp[i] = dataOut[i] * 256.0;
	}
	
	if(isNN)
	{
		for(int i = 8; i < BLOCK_SIZE; ++i)
		{
			Temp[i] = 0.0;
		}
	}

	outputBuffer = huffman(componentId, outputBuffer);

	return outputBuffer;
}