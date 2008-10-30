#ifndef __ENKF_CONFIG_NODE_H__
#define __ENKF_CONFIG_NODE_H__
#ifdef __cplusplus
extern "C" {
#endif
#include <enkf_types.h>
#include <enkf_macros.h>

typedef void   (config_free_ftype)                (void *);
typedef void   (config_activate_ftype)            (void * , active_mode_type , void *);

typedef struct enkf_config_node_struct enkf_config_node_type;

enkf_config_node_type * enkf_config_node_alloc(enkf_var_type         ,
					       enkf_impl_type        ,
					       const char          * ,
					       const char          * , 
					       const char          * , 
					       const void          * ,
					       config_free_ftype   * , 
					       config_activate_ftype *);


void 		  enkf_config_node_free(enkf_config_node_type * );
bool              enkf_config_node_include_type(const enkf_config_node_type * , int );
int  		  enkf_config_node_get_serial_size(enkf_config_node_type *, int *);
bool 		  enkf_config_node_include_type(const enkf_config_node_type * , int);
enkf_impl_type    enkf_config_node_get_impl_type(const enkf_config_node_type *);
enkf_var_type     enkf_config_node_get_var_type(const enkf_config_node_type *);
const void     *  enkf_config_node_get_ref(const enkf_config_node_type * );
const char     *  enkf_config_node_get_key_ref(const enkf_config_node_type * );
const char     *  enkf_config_node_get_outfile_ref(const enkf_config_node_type * );


VOID_FREE_HEADER(enkf_config_node);
#ifdef __cplusplus
}
#endif
#endif
