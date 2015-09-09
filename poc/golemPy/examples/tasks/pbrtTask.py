import os
import glob
import cPickle as pickle
import zlib
import subprocess
import platform, psutil
import tempfile
import shutil
import sys

############################
def format_pbrt_cmd(renderer, start_task, end_task, total_tasks, num_subtasks, num_cores, outfilebasename, scenefile):
    return ["{}".format(renderer), "--starttask", "{}".format(start_task), "--endtask", "{}".format(end_task),
            "--outresultbasename", "{}".format(outfilebasename),  "--totaltasks",  "{}".format(total_tasks),
            "--ncores", "{}".format(num_cores), "--subtasks", "{}".format(num_subtasks), "{}".format(scenefile)]

############################
def return_data(files):
    res = []
    for f in files:
        with open(f, "rb") as fh:
            file_data = fh.read()
        file_data = zlib.compress(file_data, 9)
        res.append(pickle.dumps((os.path.basename(f), file_data)))

    return { 'data': res, 'result_type': 0 }

############################
def return_files(files):
    copy_path = os.path.normpath(os.path.join(tmp_path, ".."))
    for f in files:
        shutil.copy2(f, copy_path)

    files = [ os.path.normpath(os.path.join(copy_path, os.path.basename(f))) for f in files]
    return {'data': files, 'result_type': 1 }

############################
def is_windows():
    return sys.platform == 'win32'

def exec_cmd(cmd, nice=20):
    pc = subprocess.Popen(cmd)
    if is_windows():
        import win32process
        win32process.SetPriorityClass(pc._handle, win32process.IDLE_PRIORITY_CLASS)
    else:
        p = psutil.Process(pc.pid)
        p.nice(nice)

    pc.wait()

def make_tmp_file(scene_dir, scene_src):
    if is_windows():
        tmp_scene_file = tempfile.TemporaryFile(suffix = ".pbrt", dir = scene_dir)
        tmp_scene_file.close()
        f = open(tmp_scene_file.name, 'w')
        f.write(scene_src)
        f.close()

        return tmp_scene_file.name
    else:
        tmp_scene_file = os.path.join(scene_dir, "tmp_scene_file.pbrt")
        f = open(tmp_scene_file, "w")
        f.write(scene_src)
        f.close()
        return tmp_scene_file


############################f = 
def run_pbrt_task(path_root, start_task, end_task, total_tasks, num_subtasks, num_cores, outfilebasename, scene_src, scene_dir, pbrt_path):
    pbrt = pbrt_path

    output_files = os.path.join(tmp_path, outfilebasename)

    files = glob.glob(output_files + "*.exr")

    for f in files:
        os.remove(f)


    tmp_scene_file = make_tmp_file(scene_dir, scene_src)

    if os.path.exists(tmp_scene_file):
        cmd = format_pbrt_cmd(pbrt, start_task, end_task, total_tasks, num_subtasks, num_cores, output_files, tmp_scene_file)
    else:
        print "Scene file does not exist"
        return {'data': [], 'result_type': 0 }
        
    print cmd
    prev_dir = os.getcwd()
    os.chdir(scene_dir)

    exec_cmd(cmd)

    os.chdir(prev_dir)

    print output_files

    files = glob.glob(output_files + "*.exr")

    return return_data(files)


output = run_pbrt_task(path_root, start_task, end_task, total_tasks, num_subtasks, num_cores, outfilebasename, scene_file_src, scene_dir, pbrt_path)
        