"""Generate a method table file,
initializing with the built-in methods.

The method table is used in class loading
to load method addresses into vtables. It is
not used during vm program execution.
"""

import datetime

PROLOG = f"""/* GENERATED ON {datetime.datetime.now()} by {__name__}
DO NOT EDIT BY HAND.  REGENERATE INSTEAD. 
*/

struct method_address_table_struct {
    char *method_name;
    
}
"""