#!/bin/bash

function compare {
    if [ "`diff ${1%.*}.output ${1%.*}.output1`" == "" ]
    then
        echo " ...$(tput bold)OK$(tput sgr0)"
    else
        echo " ...$(tput sgr0)$(tput bold)$(tput setaf 1)FAIL$(tput sgr0)"
    fi
}

function compile {
    for i in $ROOT_DIR/$1/*.lat; do
        echo `basename $i`;
        $ROOT_DIR/latc.py $i
    done
}

function run {
    for i in $ROOT_DIR/$1/*.out; do
        echo  -ne "$(tput setaf 2)`basename $i`"
        $i > ${i%.*}.output1 
        compare $i
        rm ${i%.*}.output1
    done
}

GOOD_DIR=tests/lattests/good
ARRAYS_DIR=tests/lattests/extensions/arrays1
STRUCT_DIR=tests/lattests/extensions/struct
OBJECTS1_DIR=tests/lattests/extensions/objects1
OBJECTS2_DIR=tests/lattests/extensions/objects2

Echo "$(tput sgr 0 1)$(tput bold)$(tput setaf 4)COMPILING TESTS$(tput sgr0)"

compile $GOOD_DIR
compile $ARRAYS_DIR 
compile $STRUCT_DIR
compile $OBJECTS1_DIR
compile $OBJECTS2_DIR

echo "$(tput sgr 0 1)$(tput bold)$(tput setaf 4)RUNNING GOOD TESTS$(tput sgr0)"

counter=1
for i in $ROOT_DIR/tests/lattests/good/*.out; do
    echo  -ne "$(tput setaf 2)`basename $i`"
    if [ $counter -eq 18 ]
    then
        $i < ${i%.*}.input > ${i%.*}.output1
    else
        $i > ${i%.*}.output1
    fi
    compare $i
    rm ${i%.*}.output1
    counter=$(($counter + 1))
done

echo "$(tput sgr 0 1)$(tput bold)$(tput setaf 4)RUNNING ARRAYS TESTS$(tput sgr0)"

run $ARRAYS_DIR

echo "$(tput sgr 0 1)$(tput bold)$(tput setaf 4)RUNNING STRUCTS TESTS$(tput sgr0)"

run $STRUCT_DIR

echo "$(tput sgr 0 1)$(tput bold)$(tput setaf 4)RUNNING OBJECTS TESTS - PART 1$(tput sgr0)"

run $OBJECTS1_DIR

echo "$(tput sgr 0 1)$(tput bold)$(tput setaf 4)RUNNING OBJECTS TESTS - PART 2$(tput sgr0)"

run $OBJECTS2_DIR

echo "$(tput bold)$(tput setaf 4)COMPILING BAD TESTS$(tput sgr0)"

for i in $ROOT_DIR/tests/lattests/bad/*.lat; do
    echo "$(tput setaf 1)`basename $i`$(tput sgr0)"
    $ROOT_DIR/latc.py $i
done


