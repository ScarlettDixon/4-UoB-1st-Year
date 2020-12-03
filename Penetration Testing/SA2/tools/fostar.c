/* FosTAR - Foscam TAR utility
 * Copyright (C) 2010 Kyle Mallory <kylemallory@yahoo.com>
 *
 * This source code is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Public License as published 
 * by the Free Software Foundation; either version 2 of the License,
 * or (at your option) any later version.
 *
 * This source code is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * Please refer to the GNU Public License for more details.
 *
 * You should have received a copy of the GNU Public License along with
 * this source code; if not, write to:
 * Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 *
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <getopt.h>

#ifdef LIBZIP  // building this requires libzip
#include <zip.h>
#endif

typedef struct hdr {
	char magic[4];
	int res1, res2;
	int size1, size2;
} hdr_t;

void unpackage_file(FILE *src, char *dst_file, long len) {
FILE *dst = NULL;
char *data = NULL;
long max_data = 0;
	
	if ( (dst = fopen(dst_file, "wb")) == NULL) {
		fprintf(stderr, "Unable to open file for writing: %s", dst_file);
		exit(-1);
	}

	if (len > max_data) {
		data = realloc(data, len);
		max_data = len;
		if (data == NULL) {
			fprintf(stderr, "Unable to allocate data necessary to extract file.  Requested: %ld bytes.\n", len);
			exit(-1);
		}
	}
	fread(data,1,len,src);

	fprintf(stdout, "Extracting %s (%ld bytes)...\n", dst_file, len);
	fwrite(data, 1, len, dst);
	fclose(dst);
}

/**
 * unpackages the firmware image into the linux.bin and the romfs.img
 */
void unpackage(char *filename) {
FILE *src = NULL;
long filelen = 0;
void *filedata = NULL;
hdr_t hdr;

	if ( ( src = fopen(filename, "rb")) == NULL) {
		fprintf(stderr, "Unable to open file for reading: %s\n", filename);
		exit(-1);
	}
	
	fseek(src, 0, SEEK_END);
	filelen = ftell(src);
	fseek(src, 0, SEEK_SET);
	
	if ( fread(&hdr, 1, sizeof(hdr_t), src) != sizeof(hdr_t)) {
		fprintf(stderr, "Error reading file header.\n");
		exit(-1);
	}
	
	if ( filelen != (hdr.size1 + hdr.size2 + sizeof(hdr_t)) ) {
		fprintf(stderr, "File size (%ld) doesn't match the reported header sizes (%ld).  File may be corrupt.\n",
			filelen, (long)(hdr.size1 + hdr.size2 + sizeof(hdr_t)) );
		exit(-1);
	}
	
	// for sanity sake
	fseek(src, sizeof(hdr_t), SEEK_SET);
	unpackage_file(src, "linux.zip", hdr.size1);
	
	// for sanity sake
	fseek(src, sizeof(hdr_t) + hdr.size1, SEEK_SET);
	unpackage_file(src, "romfs.img", hdr.size2);
	
	fclose(src);
}

int filesize(char *filename) {
FILE *f = NULL;
int len = -1;

	if ( ( f = fopen(filename, "rb")) == NULL) {
		fprintf(stderr, "Unable to open file for writing: %s\n", filename);
		exit(-1);
	} else {
		fseek(f, 0, SEEK_END);
		len = ftell(f);
		fseek(f, 0, SEEK_SET);
		fclose(f);
	}
	
	return len;
}

int package_file(FILE *dst, char *src_file) {
FILE *src = NULL;
char *data = NULL;
long max_data = 0, len = 0;
	
	len = filesize(src_file);
	
	if ( (src = fopen(src_file, "rb")) == NULL) {
		fprintf(stderr, "Unable to open file for writing: %s", src_file);
		exit(-1);
	}
	
	if (len > max_data) {
		data = realloc(data, len);
		max_data = len;
		if (data == NULL) {
			fprintf(stderr, "Unable to allocate data necessary to pack file.  Requested: %ld bytes.\n", len);
			exit(-1);
		}
	}
	fread(data,1,len,src);
	fprintf(stdout, "Packing %s (%ld bytes)...\n", src_file, len);
	fwrite(data, 1, len, dst);
	
	fclose(src);
	
	return len;
}

void package(char *dstfile, char *linux_file, char *romfs_file) {
FILE *src = NULL, *limg = NULL, *rimg = NULL;
hdr_t hdr = { "BNEG", 1, 1, 0, 0 };

	// get the file sizes of the two images
	hdr.size1 = (linux_file != NULL) ? filesize(linux_file) : 0;
	hdr.size2 = (romfs_file != NULL) ? filesize(romfs_file) : 0;

	if ( ( src = fopen(dstfile, "wb")) == NULL) {
		fprintf(stderr, "Unable to open file for writing: %s\n", dstfile);
		exit(-1);
	}
	
	if ( fwrite(&hdr, 1, sizeof(hdr_t), src) != sizeof(hdr_t)) {
		fprintf(stderr, "Error writing file header.\n");
		exit(-1);
	}

	if (linux_file)
		package_file(src, linux_file);
	
	if (romfs_file)
		package_file(src, romfs_file);
	
	fclose(src);
}

void assemble_file(char *filepath, FILE *dst) {
	FILE *src = NULL;
	int filelen = 0;
	void *filedata = NULL;
	
	if ( (src = fopen(filepath, "rb")) == NULL) {
		fprintf(stderr, "Unable to open file for reading: %s\n", filepath);
		exit(-1);
	}
	
	fseek(src, 0, SEEK_END);
	filelen = ftell(src);
	fseek(src, 0, SEEK_SET);
	
	filedata = malloc(filelen);
	if (filedata == NULL) {
		fprintf(stderr, "Not enough memory.  File too large? (Requested %d bytes)\n", filelen);
		exit(-1);
	}
	
	fwrite(&filelen, 1, 4, dst);
	if (fread(filedata, 1, filelen, src) == filelen)
		fwrite(filedata, 1, filelen, dst);
	
	free(filedata);

	fclose(src);
}

void assemble_dir(char *prefix, char *path, FILE *dst) {
DIR *dp = NULL;
struct dirent *ep;
char filename[512], pathname[512];
int pathlen = 0;
	
	if ( (dp = opendir(path)) == NULL) {
		fprintf(stderr, "Unable to open directory for reading: %s\n", path);
		exit(-1);
	}

	while ( (ep = readdir(dp)) != NULL) {
		if (!strcmp(ep->d_name, ".") ||
			!strcmp(ep->d_name, "..") ||
			!strcmp(ep->d_name, ".DS_Store") )
			continue;
		sprintf(filename, "%s/%s", path, ep->d_name);
		sprintf(pathname, "%s%s", prefix, ep->d_name);
		pathlen = strlen(pathname);
		
		fprintf(stdout, "Adding %s...\n", pathname);
		fwrite(&pathlen, 1, 4, dst);
		fwrite(pathname, 1, pathlen, dst);
		
		if (ep->d_type == DT_DIR) {
			fputc(0, dst);
			strcat(pathname, "/");
			assemble_dir(pathname, filename, dst);
		} else if (ep->d_type == DT_REG) {
			fputc(1, dst);
			assemble_file(filename, dst);
		}
	}
}

int assemble(char *dst_filename, char *src_path, char *path_prefix, char firmware[4], char* action) {
FILE *f = NULL;
char command[22];
DIR *dp;
struct dirent *ep;
int filesize = 0;
	
	fprintf(stdout, "Assembling firmware file '%s' from '%s'\n", dst_filename, src_path);	

	if ( (f = fopen(dst_filename, "wb")) == NULL)
		exit(-1);
				  
	// leave a hole for the final filesize:
	fwrite(&filesize, 1, 4, f);
	fwrite(firmware, 1, 4, f);

	sprintf(command, "%21.21s", action);
	fwrite(command, 1, 21, f);
	
	// scan the path specified by argv[3], and append all of the files into the file specified by argv[1], marking firmware num by argv[2] ('255.255.255.255');
	assemble_dir(path_prefix, src_path, f);
	
	// go back and fill in the filesize in the header
	filesize = ftell(f);
	fseek(f, 0, SEEK_SET);
	fwrite(&filesize, 1, 4, f);
	
	// go back to the end before closing (some systems, if you don't will truncate the file at the current position when you close it).
	fseek(f, filesize, SEEK_SET);
	fclose(f);
	return 0;
}

int disassemble(char *org_file, char *dst_path) {
FILE *f = NULL, *f2 = NULL;
int len = 0, type = 0, file_len = 0, file_ver = 0;
char src_file[512], dst_file[512], *data = NULL;
int max_data = 0;

	fprintf(stdout, "Disassembling firmware file '%s' to '%s'\n", org_file, dst_path);

	if ( (f = fopen(org_file, "rb")) == NULL) {
		fprintf(stderr, "Unable to open file: %s\n", org_file);
		exit(-1);
	}

	fseek(f, 0, SEEK_END);
	file_len = ftell(f);
	fseek(f, 0, SEEK_SET);

	// between firmware 2.4.8.12 and 2.4.8.14, the file format changed just slightly.
	// >= 2.4.8.14, an additional 8 bytes were added at the start of the file, and the
	// 20-character description was removed.

	fread(&len, 1, 4, f);
	if (len == file_len) {
		file_ver = 1;
	} else {
		fread(&len, 1, 4, f); // who knows what this is for.. skip it!
		fread(&len, 1, 4, f); // this is the known position for the file size in the v2 file
		if (len == file_len) {
			file_ver = 2;
		}
	}

	if (file_ver == 1) {
		fseek(f, 0x1D, SEEK_SET); // seek to first file (in v1 file)
	} else if (file_ver == 2) {
		fseek(f, 0x10, SEEK_SET); // seek to first file (in v2 file);
	} else {
		fprintf(stderr, "Unable to determine the type of file.  The header did not look like anything I expect.\n");
		exit(-1);
	}

	while(!feof(f)) {
		memset(src_file, 0, sizeof(src_file));
		memset(dst_file, 0, sizeof(dst_file));

		fread(&len, 1, 4, f); // read filename length
		fread(src_file,1,len,f); // read filename
		sprintf(dst_file, "%s%s", dst_path, src_file);

		type = 0;
		fread(&type, 1, 1, f); // read entry type 
		if (type == 0) {
			if (mkdir(dst_file, 0770) != 0) {
				fprintf(stderr, "Unable to write file: %s", dst_file);
				exit(-1);
			}
		} else if (type == 1) {
			f2 = fopen(dst_file, "wb");
			if (f2 == NULL) {
				fprintf(stderr, "Unable to write file: %s", dst_file);
				exit(-1);
			}

			fread(&len, 1, 4, f); // read data length
			if (len > max_data) {
				data = realloc(data, len);
				max_data = len;
				if (data == NULL) {
					fprintf(stderr, "Unable to allocate  data necessary to extract file.  Requested: %d bytes.\n", len);
					exit(-1);
				}
			}
			fread(data,1,len,f);

			fprintf(stdout, "Extracting %s (%d bytes)...\n", src_file, len);
			fwrite(data, 1, len, f2);
			fclose(f2);
		}
	}

	fclose(f);
	free(data);
	return 0;
}

char *g_file;
char *g_path;
char g_firmware[4] = { 255, 255, 255, 255 };
char *g_action = "UPGRADE APP_WARE FILE";
char *g_prefix = "/";
char *g_linux = NULL;
char *g_romfs = NULL;
int do_extract = 1;

static struct option long_options[] = {
{"create", no_argument, 0, 'c'},
{"extract", no_argument, 0, 'x'},
{"unpack", no_argument, 0, 'u'},
{"pack", no_argument, 0, 'k'},
{"prefix", optional_argument, 0, 'p'},
{"action", optional_argument, 0, 'a'},
{"linux", optional_argument, 0, 'l'},
{"romfs", optional_argument, 0, 'r'},
{"version", optional_argument, 0, 'v'},
{0, 0, 0, 0}
};

void usage() {
	fprintf(stderr, "fostar is a special purpose archive utility written to extract and create the firmware\n"
			"files use by the Foscam FI8908W cameras.  fostar can be ran in any one of the four operating\n"
			"modes, described below:\n\n");
	fprintf(stderr, "CREATE a new WebUI Firmware file (-c, --create)\n\n");
	fprintf(stderr, "    The following options are only valid when creating/assembling a WebUI firmware file:\n\n");
	fprintf(stderr, "    --version=#.#.#.#     the file version number for the created file (# = 0-255)\n");
	fprintf(stderr, "    --prefix=<path>       an alternate path prefix for the contents of the newly\n"
			"                          created file.  ** USE WITH CAUTION **\n");
	fprintf(stderr, "    --action=<command>    the update command for the created file. **DON'T USE THIS**\n");
	fprintf(stderr, "    <filename>            the file name of the file to create.\n");
	fprintf(stderr, "    <path>                the path to the directory containing the files to be\n"
			"                          assembled.  (Don't specify a trailing '/')\n\n");
	fprintf(stderr, "  Example:   fostar -c -v 2.4.8.13 test.bin webui_contents\n\n");
	
	fprintf(stderr, "EXTRACT the contents of the WebUI firmware file (-x, --extract)\n\n");
	fprintf(stderr, "    The following options are used when extracting the contents of a WebUI firmware file:\n\n");
	fprintf(stderr, "    <filename>            the file name of the firmware file to extract.\n");
	fprintf(stderr, "    <path>                the path to a directory where the files will be extracted\n"
			"                          to.  (Don't specify a trailing '/')\n\n");
	fprintf(stderr, "  Example:   fostar -x 2.4.8.12.bin webui_contents\n\n");
	
	fprintf(stderr, "PACK a new system firmware file (-k, --pack)\n\n");
	fprintf(stderr, "    The following options are used when packing the contents of a new system firmware file:\n\n");
	fprintf(stderr, "    --linux=<image>       the linux image to include in the firmware file.\n");
	fprintf(stderr, "    --romfs=<image>       the romfs image to include in the firmware file.\n");
	fprintf(stderr, "    <filename>            the file name of the firmware file to create.\n\n");
	fprintf(stderr, "  Example:   fostar -k -l linux.bin -r romfs.img lc_cmos_11_14_1_46.bin\n\n");

	fprintf(stderr, "UNPACK contents of the system firmware file into linunx.bin and romfs.img (-u, --unpack)\n\n");
	fprintf(stderr, "    The following options are used when unpacking the contents of a system firmware file:\n\n");
	fprintf(stderr, "    <filename>            the name of the firmware file to extract.\n\n");
	fprintf(stderr, "  Example:   fostar -u lc_cmos_11_14_1_46.bin\n\n");
	
	fprintf(stderr, "*** REMEMBER! ALWAYS KEEP A BACKUP OF YOUR ORIGINAL FIRMWARE ***\n");
	fprintf(stderr, "*** I AM NOT RESPONSIBLE FOR YOU TURNING YOUR CAMERA INTO A PAPERWEIGHT ***\n\n");
	exit(-1);
}
	
int main(int argc, char **argv) {

	fprintf(stderr, "***      REMEMBER! ALWAYS KEEP A BACKUP OF YOUR ORIGINAL FIRMWARE       ***\n");
	fprintf(stderr, "*** I AM NOT RESPONSIBLE FOR YOU TURNING YOUR CAMERA INTO A PAPERWEIGHT ***\n");
	fprintf(stderr, "***              USE OF THIS SOFTWARE IS AT YOUR OWN RISK               ***\n");
	fprintf(stderr, "***                                                                     ***\n");
	fprintf(stderr, "***           If you don't agree to this, press 'Ctrl+C' now.           ***\n");
	fgetc(stdin);
	
	while (1) {
		int option_index = 0;
		int tmp[4];
		int c = getopt_long(argc, argv, "uxckl:r:p:d:v:", long_options, &option_index);
		if (c == -1)
			break;

		switch(c) {
			case 0:
				printf ("option %s", long_options[option_index].name);
				if (optarg)
					printf (" with arg %s", optarg);
				printf ("\n");
				break;

			case 'c':
				do_extract = 0;
				break;
			case 'x':
				do_extract = 1;
				break;
			case 'u':
				do_extract = 2;
				break;
			case 'k':
				do_extract = 3;
				break;
			case 'p':
				g_prefix = strdup(optarg);
				break;
			case 'a':
				g_action = strdup(optarg);
				break;
			case 'l':
				g_linux = strdup(optarg);
				break;
			case 'r':
				g_romfs = strdup(optarg);
				break;
			case 'v':
				sscanf(optarg, "%d.%d.%d.%d", &tmp[0], &tmp[1], &tmp[2], &tmp[3]);
				g_firmware[0] = (char)tmp[0];
				g_firmware[1] = (char)tmp[1];
				g_firmware[2] = (char)tmp[2];
				g_firmware[3] = (char)tmp[3];
				break;
			case '?':
				usage();
				break;
		}
	}

	if ( (do_extract >= 2) && (optind == (argc - 1)) )
		g_file = strdup(argv[optind++]);
	else if (optind == (argc - 2)) {
		g_file = strdup(argv[optind++]);
		g_path = strdup(argv[optind++]);
	} else
		usage();


	switch (do_extract) {
	case 3:		package(g_file, g_linux, g_romfs); break;
	case 2:		unpackage(g_file); break;
	case 1:		disassemble(g_file, g_path); break;
	case 0:		assemble(g_file, g_path, g_prefix, g_firmware, g_action); break;
	default:	usage(); break;
	}
}
