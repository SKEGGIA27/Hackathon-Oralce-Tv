ls
sudo dnf install -y nc
nc -zv 10.0.0.215 2049
sudo mount -t nfs -o vers=3,tcp,nolock 10.0.0.215:/FssHackathon2026 /mnt/FssHackathon2026
mkdir /mnt/FssHackathon2026
sudo mkdir /mnt/FssHackathon2026
mkdir /mnt/FssHackathon2026
sudo mount -t nfs -o vers=3,tcp,nolock 10.0.0.215:/FssHackathon2026 /mnt/FssHackathon2026
vi /etc/fstab 
ls /etc/
ls -ltr  /etc/
sudo vi /etc/fstab 
mount -a
cd /mnt/FssHackathon2026/
ls
touch pippo.txt
cd 
cp /mnt/FssHackathon2026/report-trimestrale-consumi-forecast-enelspa-20260514T073555Z.pdf  .
ls
rm report-trimestrale-consumi-forecast-enelspa-20260514T073555Z.pdf 
cls /mnt/FssHackathon2026/
ls /mnt/FssHackathon2026/
cd /mnt/FssHackathon2026/
ls
touch ddd
mopre /etc/fstab 
more /etc/fstab 
ls
df -h
exit
python3 --version
exit
docker info
python --version
unzip hackathon_student_pack.zip -d student-pack
unzip mcp_lab.zip -d mcp-lab
unzip oci_enterprise_ai_vcstore_lab.zip -d oci-enterprise-ai-vcstore-lab
sudo dnf install python3.12 python3.12-pip python3.12-setuptools python3.12-wheel
python --version
python3.12 --version
cd mcp-lab/
python3.12 -m venv .venv
source .venv/bin/activate
pip install openai mcp uvicorn
python --version
deactivate 
rm -rf .venv
cd ..
cd oci-enterprise-ai-vcstore-lab/
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
rm -rf .venv/
python3.12 -m venv .venv
ls
source .venv/bin/activate
cd oci_enterprise_ai_vscode_lab/
ls
pip install -r requirements.txt
deactivate
cd ..
ls
ls -a
rm -rf .venv/
exit
ls
ls -la
exit
python '/home/opc/oci-enterprise-ai-vcstore-lab/oci_enterprise_ai_vscode_lab/04_streamlit_chatbot.py'
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r '/home/opc/oci-enterprise-ai-vcstore-lab/oci_enterprise_ai_vscode_lab/requirements.txt'
pip list
python '/home/opc/oci-enterprise-ai-vcstore-lab/oci_enterprise_ai_vscode_lab/04_streamlit_chatbot.py'
clear
python '/home/opc/oci-enterprise-ai-vcstore-lab/oci_enterprise_ai_vscode_lab/03_file_search_server.py'
cd oci-enterprise-ai-vcstore-lab/
cd oci_enterprise_ai_vscode_lab/

01_simple_response.py
python3 01_simple_response.py 
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r '/home/opc/oci-enterprise-ai-vcstore-lab/oci_enterprise_ai_vscode_lab/requirements.txt'
01_simple_response.py
pyhton 01_simple_response.py
python
clear
pyhton 01_simple_response.py
pyhton3.12 01_simple_response.py
01_simple_response.py
python
clear
ls
cd oci-enterprise-ai-vcstore-lab
01_simple_response.py
pyhton 01_simple_response.py
python
clear
ls
cd oci_enterprise_ai_vscode_lab
ls
pyhton 01_simple_response.py
ls
python
clear
python 01_simple_response.py
clear
ls
cd ..
ls
cd ..
ls
cd mcp-lab
ls
cd mcp
ls
clear
ls
python mcp_client.py
CLEAR
clear
python mcp_client.py
source .venv/bin/activate
ls
python '/home/opc/student-pack/hackathon_student_pack/load_vector_db.py'
pip list
cd /home/opc/student-pack/hackathon_student_pack
python3 --version && pip3 list 2>/dev/null | grep -iE "fastapi|mcp|uvicorn|pydantic" | head -20
pip3 list 2>/dev/null | head -40
pip list 2>/dev/null | head -40
python3 -m pip list 2>&1 | head -40
which python3 && ls -la /usr/local/bin/python* 2>/dev/null; ls -la /home/opc/.local/bin/ 2>/dev/null | head -10; conda --version 2>/dev/null; which pip 2>/dev/null
ls /home/opc/student-pack/hackathon_student_pack/requirements* 2>/dev/null; cat /home/opc/student-pack/hackathon_student_pack/README.md
python3 -m ensurepip --upgrade 2>&1 && python3 -m pip install --upgrade pip 2>&1 | tail -5
python3 -m pip install fastapi uvicorn pydantic python-dotenv 2>&1 | tail -10
python3 /home/opc/student-pack/hackathon_student_pack/mcp_server.py &
sleep 2 && curl -s http://127.0.0.1:8100/health | python3 -m json.tool
curl -s http://127.0.0.1:8100/health 2>&1
echo "=== TEST 1: Session Overview ===" && curl -s http://127.0.0.1:8100/tools/get_session_overview | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps({k:d[k] for k in ['total_laps_completed','latest_lap','current_compound','pit_stops_made']}, indent=2))"
echo "=== TEST 2: FL Tyre at Lap 23 ===" && curl -s "http://127.0.0.1:8100/tools/get_component_state?component=front_left_tire&lap=23" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d['data'], indent=2))"
echo "=== TEST 3: Wear Model Comparison laps 17-23 ===" && curl -s "http://127.0.0.1:8100/tools/compare_to_wear_model?corner=front_left&start_lap=17&end_lap=23" | python3 -c "import sys,json; d=json.load(sys.stdin); a=d['analysis']['front_left']; print(json.dumps({k:a[k] for k in ['max_gap_pp','max_gap_at_lap','current_status','degradation_trend','recommendation']}, indent=2))"
echo "=== TEST 4: Strategy at Lap 23 ===" && curl -s "http://127.0.0.1:8100/tools/get_strategy_context?lap=23" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d['pit_recommendation'], indent=2))"
echo "=== TEST 5: Stream Telemetry ===" && curl -s "http://127.0.0.1:8100/tools/stream_live_telemetry?cursor=0&batch_size=3" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Events: {len(d[\"events\"])}, Next cursor: {d[\"next_cursor\"]}, EOS: {d[\"end_of_stream\"]}'); print(f'Laps returned: {[e[\"lap\"] for e in d[\"events\"]]}')"
echo "=== TEST 6: Race Control Events ===" && curl -s "http://127.0.0.1:8100/tools/list_race_control_events" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Total events: {d[\"total_events\"]}'); [print(f'  Lap {e[\"lap\"]}: {e[\"type\"]} — {e[\"message\"][:60]}') for e in d['events']]"
echo "=== TEST 7: Lap Window with fields ===" && curl -s "http://127.0.0.1:8100/tools/get_lap_window?start_lap=20&end_lap=23&fields=lap_time_s,tires.wear_pct,driver_feedback" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'Lap {l[\"lap\"]}: time={l.get(\"lap_time_s\",\"?\")}s, FL wear={l.get(\"tires.wear_pct\",{}).get(\"front_left\",\"?\")}%, feedback=\"{l.get(\"driver_feedback\",\"?\")[:50]}\"') for l in d['laps']]"
echo "=== Tools Discovery ===" && curl -s "http://127.0.0.1:8100/tools" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'  {t[\"name\"]}: {t[\"endpoint\"]}') for t in d['tools']]"
kill %1 2>/dev/null; echo "Server stopped"
python3 mcp_server.py
 source /home/opc/.venv/bin/activate
/home/opc/.venv/bin/python /home/opc/mcp-lab/mcp/mcp_client.py
/home/opc/.venv/bin/python /home/opc/mcp-lab/mcp/mcp_server.py
/home/opc/.venv/bin/python /home/opc/mcp-lab/mcp/mcp_client.py
/home/opc/.venv/bin/python /home/opc/mcp-lab/mcp/mcp_server.py
/home/opc/.venv/bin/python /home/opc/mcp-lab/mcp/mcp_client.py
clear
/home/opc/.venv/bin/python /home/opc/mcp-lab/mcp/mcp_client.py
source /home/opc/.venv/bin/activate
/home/opc/.venv/bin/python -m pip install --upgrade pip
/home/opc/.venv/bin/python -m pip install "mcp[cli]" uvicorn python-dotenv
/home/opc/.venv/bin/python /home/opc/mcp-lab/mcp/mcp_client.py
clear
/home/opc/.venv/bin/python /home/opc/mcp-lab/mcp/mcp_client.py
source /home/opc/.venv/bin/activate
cd /home/opc/student-pack/hackathon_student_pack
set -a
source .env
set +a
echo $OCI_OPENAI_BASE_URL
echo $OCI_GENAI_API_KEY
echo $OCI_MODEL_ID
echo $OCI_OPENAI_BASE_URL
cleatr
exit
source .venv/bin/activate
python 
python mcp_server.py
clea
clear
ls
python asdfasfafasfsadfsa
ls
cd studentpack
ls
celar
clear
ls
cs student-pack
cd student-pack
ls
cd hackathon_student_pack
ls
python mcp_server.py
source .venv/bin/activate
ls
cd student-pack
ls
cd hackathon_student_pack
ls
python mcp_client.py
clear
streamlit run mcp_client.p
streamlit run mcp_client.py
source .venv/bin/activate
ls
cd student-pack
ls
cd hackathon_student_pack
ls
python query_vector_db.py
 source /home/opc/.venv/bin/activate
exit
 source /home/opc/.venv/bin/activate
exit
 source /home/opc/.venv/bin/activate
python query_vector_db.py
ls
cd  student-pack
ls
cd hackathon_student_pack
ls
python mcp_server.py && python mcp_client.py && python interface.py
clear
python mcp_server.py
 source /home/opc/.venv/bin/activate
cd student-pack
cd hackathon_student_pack
python mcp_client
ls
python mcp_client.py
 source /home/opc/.venv/bin/activate
cd student-pack
cd hackathon_student_pack
python interface.py
streamlit run interface.py
pip install plotly
streamlit run interface.py
cd student-pack
cd hackathon_student_pack
 source /home/opc/.venv/bin/activate
python mcp_client.py
 source /home/opc/.venv/bin/activate
python mcp_client.py
ls
cd student-pack
ls
cd hackathon_student_pack
ls
python mcp_client.py
python mcp_server.py
 source /home/opc/.venv/bin/activate
/home/opc/.venv/bin/python /home/opc/mcp-lab/mcp/mcp_client.py
source /home/opc/.venv/bin/activate
cd /home/opc/mcp-lab/mcp
/home/opc/.venv/bin/python -m uvicorn mcp_server:app --host 0.0.0.0 --port 8000
/home/opc/.venv/bin/python /home/opc/mcp-lab/mcp/mcp_client.py
clear
/home/opc/.venv/bin/python /home/opc/mcp-lab/mcp/mcp_client.py
clear
ls
cd ..
ls
 source /home/opc/.venv/bin/activate
source /home/opc/.venv/bin/activate
cd /home/opc/student-pack/hackathon_student_pack
set -a
source .env
set +a
export F1_MCP_SERVER_URL="http://localhost:8000/mcp"
/home/opc/.venv/bin/python /home/opc/mcp-lab/mcp/mcp_client.py
/home/opc/.venv/bin/python -m pip install python-dotenv
/home/opc/.venv/bin/python /home/opc/mcp-lab/mcp/mcp_client.py
clear
ls
python interface.py 
streamlit run interface.py
 source /home/opc/.venv/bin/activate
cd student 
ls -la
ls
cd student-pack/
ls
cd hackathon_student_pack/
ls
interface.py
./interface.py
python interface.py 
streamlit run interface.py
 source /home/opc/.venv/bin/activate
streamlit run interface.py
cd student-pack
cd hackathon_student_pack
streamlit run interface.py
 source /home/opc/.venv/bin/activate
 source /home/opc/.venv/bin/activate
 source /home/opc/.venv/bin/activate
