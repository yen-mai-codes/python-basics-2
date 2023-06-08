"""
Stage 1 of our fictional pipeline
"""

from subprocess import Popen, PIPE, STDOUT
file_path = '/media/yenhocdungubuntu/Main File Box/Jobs_Internship/Blueoc/Wk03/python-basics-2/bonus/mysterious_generation_script.sh'


def stage_execute(num_files: int, date: str) -> str:
    """
    Executes the stage 1.
    """
    print("Executing stage 1..")
    output = Popen([file_path, str(num_files), date], stdout=PIPE, stderr=STDOUT)
    stdout, _ = output.communicate()
    return stdout.decode("utf-8")
