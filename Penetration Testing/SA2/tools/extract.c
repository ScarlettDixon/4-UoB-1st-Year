#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

int main(int argc, char **argv) {
  FILE *f = NULL;
  int len = 0, type = 0;
  char src_file[512], dst_file[512], *data = NULL;
  int max_data = 0;

  if ( (f = fopen(argv[1], "rb")) == NULL)
    exit(-1);

  fseek(f, 0, SEEK_END);
  int file_len = ftell(f);
  fseek(f, 0, SEEK_SET);

  fread(&len, 1, 4, f);
  if (len != file_len) {
    fprintf(stderr, "File size doesn't match that reported in the header: %d/%d\n", len, file_len);
    exit(-1);
  }

  fseek(f, 29, SEEK_SET); // seek to first file

  while(!feof(f)) {
    memset(src_file, 0, sizeof(src_file));
    memset(dst_file, 0, sizeof(dst_file));

    fread(&len, 1, 4, f); // read filename length
    fread(src_file,1,len,f); // read filename
    sprintf(dst_file, "%s%s", argv[2], src_file);

    type = 0;
    fread(&type, 1, 1, f); // read entry type
    if (type == 0) {
      if (mkdir(dst_file, 0770) != 0) {
        fprintf(stderr, "Unable to write file: %s", dst_file);
        exit(-1);
      }
    } else if (type == 1) {
      FILE *f2 = fopen(dst_file, "wb");
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
