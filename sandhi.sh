mkdir dpd
cd dpd
gdown 1kp3TH1Bt5EJGODBjF3-eEB30hV9mo_HO
unzip sandhi.zip
rm sandhi.zip
md sandhi/output
pip install poetry
poetry install
poetry shell
export PYTHONPATH=$PYTHONPATH:sandhi/tools
nohup python3.10 sandhi/splitter.py &
nohup python3.10 sandhi/postprocess.py &

# scp root@164.90.237.121:/root/dpd/sandhi/output.zip output.zip

# tail -n 10 nohup.out
# ps aux | grep python
# tail -f /proc/3245/fd/1