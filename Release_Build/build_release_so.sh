#cython: language_level=3

#編譯一個釋出版本到外層
#注意!! 執行位置請於此專案rootpath執行
mkdir -p ../lib/TeaOrFish
cp -r ./ ../lib/TeaOrFish/
cd ../lib/TeaOrFish

echo "finnish copy file."



pip3 install pyinstaller
python3 setup.py build_ext --inplace

find . -name "*.c" | xargs rm -f
find . -name "*.py" ! -name "linebotApp.py" | xargs rm -f
rm -rf build

cd -


