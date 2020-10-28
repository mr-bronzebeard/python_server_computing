from flask import Flask, jsonify, request, url_for
from subprocess import Popen
from threading import Thread
from datetime import datetime
app = Flask (__name__)
task_map = {}
def spaw_task(func, args):
    task_id = datetime.now().strftime("%Y_%m_%d_%H%M")
    t = Thread(target=func, args=(args, task_id))
    t.start()
    return task_id

def omp_task(N, task_id):
    task_map[task_id] = {}
    task_map[task_id]["status"] = "STARTED"
    fname = "openmp_test_{0}.txt".format(task_id)
    output_file = open(fname, "w")
    task_map[task_id]["result_path"] = fname
    p = Popen(["omp.exe", str(N)], stdout=output_file)
    task_map[task_id]["status"] = "ENDED"

def cuda_task(N, task_id):
    task_map[task_id] = {}
    task_map[task_id]["status"] = "STARTED"
    fname = "./cuda_test_{0}.txt".format(task_id)
    task_map[task_id]["result_path"] = fname
    output_file = open(fname, "w")
    p = Popen(["./cuda/cuda", str(N)], stdout=output_file)
    task_map[task_id]["status"] = "ENDED"

@app.route("/openmp", methods=["GET", "POST"])
def get_openmp_task():
    rb = request.form.to_dict(flat=True)
    N = int(rb["N"])
    task_id = spaw_task(omp_task, N)
    return jsonify({"task_id" : task_id}),\
            202, {"Location" : url_for("taskstatus", task_id=task_id)}

@app.route("/cuda", methods=["GET", "POST"])
def get_cuda_task():
    rb = request.form.to_dict(flat=True)
    N = int(rb["N"])
    task_id = spaw_task(cuda_task, N)
    return jsonify({"task_id" : task_id}),\
            202, {"Location" : url_for("taskstatus", task_id=task_id)}

@app.route("/status/<task_id>")
def taskstatus(task_id):
    print("received task_id = ", task_id)
    response = {}
    if task_map[task_id]["status"] == "STARTED":
        response["result"] = "Processing..."
    elif task_map[task_id]["status"] == "ENDED":
        with open(task_map[task_id]["result_path"]) as res_file:
            response["result"] = res_file.read()
    return jsonify(response)

if __name__ == "__main__":
    app.run(port=8080, debug=True)
