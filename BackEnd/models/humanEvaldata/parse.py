import json, sys

def createTrainingData(y_characteristic):
    """ Creates the training data for a particular characteristic - options are for the human evaluation, 
    such as inquisitive, avoid_rep, & listen 
    Discovered only inquisitive and interest had decent variation
    """
    X_data = []
    y = []
    newData = {}
    with open("human_eval.jsonl") as f:
        lines = f.read().split("\n")
        del lines[len(lines)-1]
        for line in lines: 
            cur = json.loads(line)
            txt = ""
            for j in cur["dialog"]:
                txt+=j["text"]+" "
            X_data.append(txt)
            # on a scale of 1 - 4
            #tmp = [0 for i in range(4)]
            #tmp[cur["evaluation_results"][y_characteristic]-1] = 1
            y.append(cur["evaluation_results"][y_characteristic]-1)
    print(X_data)
    print(y)
    print(X_data[9],y[9])
    newData["X"] = X_data
    newData["y"] = y
    with open(y_characteristic+".json", "w+") as f:
        json.dump(newData, f)
        
if __name__ == '__main__':
    arg = sys.argv[1]
    createTrainingData(arg)