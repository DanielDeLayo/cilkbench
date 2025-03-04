DEFAULT_COMPILERS_TO_TEST="tapir"
DEFAULT_WORKERS_TO_TEST="1 2 4 6 8 10 12 24 48"
DEFAULT_WORKERS_TO_TEST="24 1"


TAPIR_BASE=`realpath ..`
# NUMTRIALS=3

if [ -z $REF_BASE ]; then
    if [ -z $TAPIR_BASE ]; then
	REF_BASE="/unknown/path/to/src-ref"
    else
	REF_BASE=$TAPIR_BASE-ref
    fi
fi

if [ ! -z $TAPIR_BASE ]; then
    if [ -z $DEBUG ]; then
	TAPIR_ROOT=$TAPIR_BASE/build
	REF_ROOT=$REF_BASE/build
    else
	echo "Using Debug build"
	TAPIR_ROOT=$TAPIR_BASE/build-debug
	REF_ROOT=$REF_BASE/build-debug
    fi
fi

if [ ! -z $TAPIR_ROOT ]; then
    TAPIR_PATH=$TAPIR_ROOT/bin
    REF_PATH=$REF_ROOT/bin

    TAPIR_CC=$TAPIR_PATH/clang
    TAPIR_CXX=$TAPIR_PATH/clang++

    TAPIR_LIB=$TAPIR_ROOT/lib/clang/`$TAPIR_CC --version | perl -pe '($_)=/([0-9]+([.][0-9]+)+)/'`/lib/linux
else
    TAPIR_LIB=/usr/lib/clang/`$TAPIR_CC --version | perl -pe '($_)=/([0-9]+([.][0-9]+)+)/'`/lib/linux
fi

TAPIR_ROOT=$TAPIR_BASE/build
TAPIR_PATH=$TAPIR_ROOT/bin
TAPIR_CC=$TAPIR_PATH/clang
TAPIR_CXX=$TAPIR_PATH/clang++
TAPIR_LIB=$TAPIR_ROOT/lib/clang/19/lib/x86_64-unknown-linux-gnu/

BITCODE_IAF=$(find $TAPIR_ROOT -name "*cilkiaf.bc")
BITCODE_PRACE=$(find $TAPIR_ROOT -name "*cilkprace.bc")
BITCODE_CSAN=$(find $TAPIR_ROOT -name "*cilksan.bc")
if [ ! -z "${BITCODE_IAF}" ]; then
  BITCODE_IAF="-mllvm -csi-tool-bitcode=$BITCODE_IAF"
fi
if [ ! -z "${BITCODE_PRACE}" ]; then
  BITCODE_PRACE="-mllvm -csi-tool-bitcode=$BITCODE_PRACE"
fi
if [ ! -z "${BITCODE_CSAN}" ]; then
  BITCODE_CSAN="-mllvm -csi-tool-bitcode=$BITCODE_CSAN"
fi

echo $TAPIR_LIB

#TAPIR_CILK_FLAG=-fcilkplus
TAPIR_CILK_FLAG=-fopencilk
REF_CILK_FLAG=-fcilkplus #-fdetach
GCC_CILK_FLAG=-fcilkplus

SERIAL_CFLAGS="-Dcilk_for=for -Dcilk_spawn=  -Dcilk_sync=  -D_Cilk_for=for -D_Cilk_spawn=  -D_Cilk_sync= "
REPORT_CFLAGS="-Rpass=.* -Rpass-analysis=.*"
# REPORT_CFLAGS="-Rpass=loop-spawning"

CILKSAN_LIB=$TAPIR_LIB
CILKSAN_CFLAGS="-g -fsanitize=cilk"
# CILKSAN_LDFLAGS="-lcilksan -L$CILKSAN_LIB"
CILKSAN_LDFLAGS="-fsanitize=cilk"

CILKSCALE_CFLAGS="-flto -fcsi"
CILKSCALE_LDFLAGS="-flto -fuse-ld=lld -L$TAPIR_LIB"
CILKSCALE_LDLIBS="-lclang_rt.cilkscale-x86_64"

JEMALLOC_LDLIBS="-L`jemalloc-config --libdir` -Wl,-rpath,`jemalloc-config --libdir` -ljemalloc `jemalloc-config --libs`"

C_COMPILER() {
    case $1 in
	"tapir") echo "$TAPIR_CC $TAPIR_CILK_FLAG";;
	"cilksan") echo "$TAPIR_CC $TAPIR_CILK_FLAG -fsanitize=cilk";;
	"cilkiaf") echo "$TAPIR_CC $TAPIR_CILK_FLAG -fcilktool=cilkiaf";;
	"cilkprace") echo "$TAPIR_CC $TAPIR_CILK_FLAG -fcilktool=cilkprace";;
	"cilksanprace") echo "$TAPIR_CC $TAPIR_CILK_FLAG -fsanitize=cilkprace";;
	"ref") echo "$REF_PATH/clang $REF_CILK_FLAG";;
	"stapir") echo "$TAPIR_CC $TAPIR_CILK_FLAG $SERIAL_CFLAGS";;
	"sref") echo "$REF_PATH/clang $REF_CILK_FLAG $SERIAL_CFLAGS";;
	"serial") echo "$TAPIR_CC $SERIAL_CFLAGS";;
	"gcc") echo "gcc $GCC_CILK_FLAG";;
	"sgcc") echo "gcc $GCC_CILK_FLAG $SERIAL_CFLAGS";;
	*) echo "Unknown compiler $1"; exit 1;;
    esac
}

CXX_COMPILER() {
    case $1 in
	"tapir") echo "$TAPIR_CXX $TAPIR_CILK_FLAG";;
	"cilksan") echo "$TAPIR_CXX $TAPIR_CILK_FLAG -fsanitize=cilk";;
	"cilkiaf") echo "$TAPIR_CXX $TAPIR_CILK_FLAG -fcilktool=cilkiaf";;
	"cilkprace") echo "$TAPIR_CXX $TAPIR_CILK_FLAG -fcilktool=cilkprace";;
	"cilksanprace") echo "$TAPIR_CXX $TAPIR_CILK_FLAG -fsanitize=cilkprace";;
	"ref") echo "$REF_PATH/clang++ $REF_CILK_FLAG";;
	"stapir") echo "$TAPIR_CXX $TAPIR_CILK_FLAG $SERIAL_CFLAGS";;
	"sref") echo "$REF_PATH/clang++ $REF_CILK_FLAG $SERIAL_CFLAGS";;
	"serial") echo "$TAPIR_CXX $SERIAL_CFLAGS";;
	"gcc") echo "g++ $GCC_CILK_FLAG";;
	"sgcc") echo "g++ $GCC_CILK_FLAG $SERIAL_CFLAGS";;
	*) echo "Unknown compiler $1"; exit 1;;
    esac
}

CILKFLAG() {
    case $1 in
	"tapir") echo "$TAPIR_CILK_FLAG";;
	"cilksan") echo "$TAPIR_CILK_FLAG -fsanitize=cilk $BITCODE_CSAN";;
	"cilkiaf") echo "$TAPIR_CILK_FLAG -fcilktool=cilkiaf $BITCODE_IAF";;
	"cilkprace") echo "$TAPIR_CILK_FLAG -fcilktool=cilkprace $BITCODE_PRACE";;
	"cilksanprace") echo "$TAPIR_CILK_FLAG -fsanitize=cilkprace $BITCODE_PRACE";;
	"ref") echo "$REF_CILK_FLAG";;
	"stapir") echo "$TAPIR_CILK_FLAG $SERIAL_CFLAGS";;
	"sref") echo "$REF_CILK_FLAG $SERIAL_CFLAGS";;
	"serial") echo "$SERIAL_CFLAGS";;
	"gcc") echo "$GCC_CILK_FLAG";;
	"sgcc") echo "$GCC_CILK_FLAG $SERIAL_CFLAGS";;
	*) echo "Unknown compiler $1"; exit 1;;
    esac
}

RUN_ON_P_WORKERS() {
    P=$1
    # echo "CILK_NWORKERS=$P setarch x86_64 -R taskset -c 1-$P numactl -i all ionice -c 2 -n 0 $2"
    # CILK_NWORKERS=$P setarch x86_64 -R taskset -c 1-$P numactl -i all ionice -c 2 -n 0 $2
    # echo "CILK_NWORKERS=$P setarch x86_64 -R taskset -c 1-$P numactl -i all ionice -c 2 -n 0 $2"
    # CILK_NWORKERS=$P setarch x86_64 -R taskset -c 1-$P numactl -i all ionice -c 2 -n 0 $2
    echo "CILK_NWORKERS=$P setarch `uname -m` -R taskset -c 0-$(expr $P - 1) numactl -i all ionice -c 2 -n 0 $2"
    CILK_NWORKERS=$P setarch `uname -m` -R taskset -c 0-$(expr $P - 1) numactl -i all ionice -c 2 -n 0 $2
}
