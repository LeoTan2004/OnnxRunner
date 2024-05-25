uname -a
cd deploy/
target=onnx_profile
pyinstaller ${target}.py
sed -i '1iimport sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)' ${target}.spec
pyinstaller ${target}.spec
cp -r ./model_data ./dist/${target}
