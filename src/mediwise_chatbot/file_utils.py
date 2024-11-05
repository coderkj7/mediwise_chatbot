import json
import os

def convert_json_file(filewithpath):
    
    with open(filewithpath,encoding="utf-8") as f:
        data = json.load(f)
        data = data.replace(' ', '').replace('\n', '')
        res = ''.join(data)
        res_json = json.dumps(res)
        cmd_res = os.system(f"echo {res_json} | jq -c '.[]' > {filewithpath}")
    return cmd_res


def process_json_data(filewithpath):
    with open(filewithpath) as f:
        lines = f.readlines()
        for l in lines:
            d = json.loads(l)
            d = list(d.values())
            print(f"('{d[0]}','{d[1]}','{d[2]}','{d[3]}','{d[4]}'),")
        

# convert_json_file('../../data/doctor_data.json')
# process_json_data('../../data/doctor_data.json')