for i in lattests/good/*.out; do
    echo $i;./$i > ${i%.*}.output1;
    diff ${i%.*}.output ${i%.*}.output1;
    rm ${i%.*}.output1
done
