#ifndef __BLOCK_FS_DRIVER_H__
#define __BLOCK_FS_DRIVER_H__


#include <stdio.h>
#include <fs_types.h>
#include <stdbool.h>

typedef struct block_fs_driver_struct block_fs_driver_type;


void                   block_fs_driver_fwrite_mount_info(FILE * stream , fs_driver_type driver_type );
block_fs_driver_type * block_fs_driver_fread_alloc(const char * root_path , FILE * stream);





#endif