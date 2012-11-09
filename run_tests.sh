#!/bin/bash
GOOD_FILES=lattests/good/*.lat
for i in $GOOD_FILES; do
    if [[ `./testLatte $i | grep Succesful` != "Parse Succesful!" ]]; then
        echo "ERROR: test $i failed!"
        exit 1
    fi
done

echo "Tests from catalogue <<good>> passed!"

BAD_FILES=lattests/bad/*.lat
mkfifo tmp
for i in $BAD_FILES; do
    TMP=`./testLatte $i 2>tmp 1>/dev/null | grep "error" tmp | cut -d" " -f1`
    echo $TMP
    if [[ $TMP != "error:" ]]; then
        echo "ERROR: test $i failed!"
        rm tmp
        exit 1
    fi
done
rm tmp
echo "Tests from catalogue <<bad>> passed!"

