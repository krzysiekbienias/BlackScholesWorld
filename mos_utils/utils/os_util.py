import shlex
import socket
from subprocess import PIPE,Popen


def run_os_cmd(arg_cmd):
    """
    This function runs the os command and capturers the output and error streams the both output and error returned as result
    """
    args=shlex.split(arg_cmd)
    process_to_run=Popen(args,stdout=PIPE,stderr=PIPE,stdin=PIPE)
    out_buffer,errors=process_to_run.communicate()
    out_str=out_buffer.decode()
    out_str=out_str.rstrip()
    return out_str,errors

def get_unix_cred(arg_alias):
    """This function returns the credentials for the given Cloakware alias
    Arguments:
         arg_alias{[str]} -- [CloakWare Alias]
    Raises:
          RuntimeError: [description]
    """
    cwa_exe='adres/get_cloakware-credentials.sh{0}'.format(arg_alias)
    out_str,err=run_os_cmd(cwa_exe)
    space_pos=out_str.find(' ')
    if space_pos!=-1:
        user_name,password=out_str.split(' ')
    else:
        err_msg='Failed to get credentials: Error:'+out_str
        raise RuntimeError(err_msg)
    return user_name,password

def get_server_env():
    host_server_name=socket.gethostname
    if any(name in host_server_name.upper() for name in [])

