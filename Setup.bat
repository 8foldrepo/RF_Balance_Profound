::Install GClib assuming the default installation path
cd %temp%
mkdir py
cd py
copy "c:\Program Files (x86)\Galil\gclib\source\wrappers\python"
copy "c:\Program Files (x86)\Galil\gclib\examples\python"
python setup.py install