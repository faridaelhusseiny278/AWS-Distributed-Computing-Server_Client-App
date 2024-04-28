# try:
#             batch_commands= [
#             rf'gcc --coverage {filename}',
#             'a.exe',
#             rf'gcov {filename} > gcov_output.txt 2>&1',
#             rf'copy {filename}.gcov coverage_report.txt'
#             ]
#             for cmd in batch_commands:
#                 subprocess.run(cmd, shell=True, check=True)
#             print("batch Commands executed successfully.")
            
#  except subprocess.CalledProcessError as e:
#             print("Error: Failed to execute the batch file")
#             print(e)
#             return -1