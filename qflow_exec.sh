#!/bin/tcsh -f
#-------------------------------------------
# qflow exec script for project /data
#-------------------------------------------

/usr/local/share/qflow/scripts/yosys.sh /data ibex_top /data/source/ibex_top.sv || exit 1
/usr/local/share/qflow/scripts/graywolf.sh -d /data ibex_top || exit 1
/usr/local/share/qflow/scripts/vesta.sh  /data ibex_top || exit 1
/usr/local/share/qflow/scripts/qrouter.sh /data ibex_top || exit 1
/usr/local/share/qflow/scripts/vesta.sh  -d /data ibex_top || exit 1
/usr/local/share/qflow/scripts/magic_db.sh /data ibex_top || exit 1
/usr/local/share/qflow/scripts/magic_drc.sh /data ibex_top || exit 1
/usr/local/share/qflow/scripts/netgen_lvs.sh /data ibex_top || exit 1
/usr/local/share/qflow/scripts/magic_gds.sh /data ibex_top || exit 1
# /usr/local/share/qflow/scripts/cleanup.sh /data ibex_top || exit 1
# /usr/local/share/qflow/scripts/cleanup.sh -p /data ibex_top || exit 1
# /usr/local/share/qflow/scripts/magic_view.sh /data ibex_top || exit 1
