
from infraed_huihe.infraedapi import InfraedApi
platform=""
infraed = InfraedApi()
infraed.init()
device={
  "entity_id": "light.infraed_2",
  "key_id": 5,
"irdata": "000000000000"
 #"irdata": "1367,407,1368,407,443,1269,1371,407,1343,433,1342,433,1343,433,417,1296,419,1273,442,1297,418,1297,418,7816,1343,435,1340,433,416,1298,1343,433,1342,434,1342,433,1343,433,416,1298,417,1272,521,1211,426,1297,418,7786,1340,443,1332,433,416,1297,1446,331,1342,433,1342,433,1342,433,417,1297,419,1297,418,1274,442,1296,419,7815,1344,432,1343,433,417,1296,1345,433,1342,432,1343,433,1343,432,417,1296,445,1270,447,1270,443,1270,444"

}
# "irdata": "1367,407,1368,407,443,1269,1371,407,1343,433,1342,433,1343,433,417,1296,419,1273,442,1297,418,1297,418,7816,1343,435,1340,433,416,1298,1343,433,1342,434,1342,433,1343,433,416,1298,417,1272,521,1211,426,1297,418,7786,1340,443,1332,433,416,1297,1446,331,1342,433,1342,433,1342,433,417,1297,419,1297,418,1274,442,1296,419,7815,1344,432,1343,433,417,1296,1345,433,1342,432,1343,433,1343,432,417,1296,445,1270,447,1270,443,1270,444"

device1={
 "device_name": "learning light",
 "device_type": "light",
 "kfid": -1,
 "keylist": [{
   "1": "199,200,198"
  },
  {
   "2": "199,200,198"
  },
  {
   "3": "199,200,198"
  }
 ]
}

device2={"entity_id":"light.infraed_1"}
#device_list = infraed.add_new_device(device1)
device_list = infraed.device_control(1,"电源")
#print("device_list:",device_list)


