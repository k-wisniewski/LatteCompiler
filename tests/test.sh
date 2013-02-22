echo "COMPILING TESTS"

for i in tests/lattests/good/*.lat; do
    echo `basename $i`
    ./latc.py $i
done

echo "RUNNING TESTS"

counter=1
for i in tests/lattests/good/*.class; do
    echo `basename $i`
    if [ $counter -eq 18 ]
    then
        java -cp lib/:tests/lattests/good/ `basename ${i%.*}` < ${i%.*}.input > ${i%.*}.output1 
    else
        java -cp lib/:tests/lattests/good/ `basename ${i%.*}` > ${i%.*}.output1
    fi
    diff ${i%.*}.output1 ${i%.*}.output
    rm ${i%.*}.output1
    counter=$(($y + 1))
done
