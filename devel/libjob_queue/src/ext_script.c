/*
   Copyright (C) 2012  Statoil ASA, Norway. 
    
   The file 'ext_script.c' is part of ERT - Ensemble based Reservoir Tool. 
    
   ERT is free software: you can redistribute it and/or modify 
   it under the terms of the GNU General Public License as published by 
   the Free Software Foundation, either version 3 of the License, or 
   (at your option) any later version. 
    
   ERT is distributed in the hope that it will be useful, but WITHOUT ANY 
   WARRANTY; without even the implied warranty of MERCHANTABILITY or 
   FITNESS FOR A PARTICULAR PURPOSE.   
    
   See the GNU General Public License at <http://www.gnu.org/licenses/gpl.html> 
   for more details. 
*/

#include <stdbool.h>
#include <stdlib.h>
#include <dlfcn.h>

#include <int_vector.h>
#include <util.h>
#include <type_macros.h>
#include <stringlist.h>
#include <arg_pack.h>
#include <vector.h>

#include <config.h>

#include <ext_cmd.h>
#include <ext_script.h>


#define CMD_TYPE_ID           66153
#define EXT_SCRIPT_TYPE_ID  6762081

typedef struct cmd_struct {
  UTIL_TYPE_ID_DECLARATION;
  const ext_cmd_type * ext_cmd;
  stringlist_type    * arglist;
} cmd_type;





struct ext_script_struct {
  UTIL_TYPE_ID_DECLARATION;
  time_t                 compile_time;
  bool                   compiled;
  char                 * src_file; 
  config_type          * config_compiler;
  vector_type          * cmd_list;
};

/*****************************************************************/

static cmd_type * cmd_alloc( const ext_cmd_type * ext_cmd , const stringlist_type * arglist) {
  cmd_type * cmd = util_malloc( sizeof * cmd );
  UTIL_TYPE_ID_INIT(cmd , CMD_TYPE_ID );
  cmd->ext_cmd = ext_cmd;
  cmd->arglist = stringlist_alloc_deep_copy( arglist );
  return cmd;
}

static UTIL_SAFE_CAST_FUNCTION( cmd , CMD_TYPE_ID );

static void cmd_free( cmd_type * cmd ){ 
  stringlist_free( cmd->arglist );
  free( cmd );
}

static void cmd_free__( void * arg ) {
  cmd_type * cmd = cmd_safe_cast( arg );
  cmd_free( cmd );
}

/*****************************************************************/


static bool ext_script_try_compile( ext_script_type * script ) {
  if (util_file_exists( script->src_file )) {
    time_t src_mtime = util_file_mtime( script->src_file );
    if (script->compiled && (util_difftime( src_mtime , script->compile_time , NULL , NULL , NULL, NULL) > 0 ))
      // Script is already up to date.
      return true;
    else {
      // Try to compile
      script->compiled = false;
      vector_clear( script->cmd_list );
      
      return true;
    }
  } else
    return script->compiled;  // It is legal to remove the script after 
                              // successfull compilation.
}


ext_script_type * ext_script_alloc( const char * src_file , config_type * config_compiler) {
  ext_script_type * script = util_malloc( sizeof * script );
  UTIL_TYPE_ID_INIT( script , EXT_SCRIPT_TYPE_ID );

  script->src_file        = util_alloc_string_copy( src_file );
  script->config_compiler = config_compiler;
  script->cmd_list        = vector_alloc_new();
  script->compiled        = false;
  
  ext_script_try_compile( script );

  return script;
}