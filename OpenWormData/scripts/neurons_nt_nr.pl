#Original Code by Dimitar Shterionov from
# Shterionov, D. S., & Janssens, G. (2011). Data acquisition and modeling for
#learning and reasoning in probabilistic logic environment. In EPIA 2011
#(pp. 978–989). Retrieved from https://lirias.kuleuven.be/bitstream/123456789/316487/3/EPIA2011_p_298-312_166.pdf

#Modified and adapted by the OpenWorm project
:-use_module(library(lists)).

#Original connectome -- this is not updated to most recent 2015 version.
synapse('ADAL', 'ADAR', 1).
synapse('ADAL', 'ADFL', 1).
synapse('ADAL', 'AIBL', 1).
synapse('ADAL', 'AIBR', 2).
synapse('ADAL', 'ASHL', 1).
synapse('ADAL', 'AVAR', 2).
synapse('ADAL', 'AVBL', 4).
synapse('ADAL', 'AVBR', 2).
synapse('ADAL', 'AVBR', 5).
synapse('ADAL', 'AVDL', 1).
synapse('ADAL', 'AVDR', 2).
synapse('ADAL', 'AVEL', 1).
synapse('ADAL', 'AVJR', 5).
synapse('ADAL', 'FLPR', 1).
synapse('ADAL', 'PVQL', 1).
synapse('ADAL', 'RICL', 1).
synapse('ADAL', 'RICL', 1).
synapse('ADAL', 'RICR', 1).
synapse('ADAL', 'RIML', 3).
synapse('ADAL', 'RIPL', 1).
synapse('ADAL', 'SMDVR', 2).
synapse('ADAR', 'ADAL', 1).
synapse('ADAR', 'ADFR', 1).
synapse('ADAR', 'AIBL', 1).
synapse('ADAR', 'AIBR', 1).
synapse('ADAR', 'ASHR', 1).
synapse('ADAR', 'AVAL', 1).
synapse('ADAR', 'AVBL', 1).
synapse('ADAR', 'AVBL', 1).
synapse('ADAR', 'AVBR', 5).
synapse('ADAR', 'AVDL', 2).
synapse('ADAR', 'AVEL', 1).
synapse('ADAR', 'AVJL', 1).
synapse('ADAR', 'AVJL', 2).
synapse('ADAR', 'PVQR', 1).
synapse('ADAR', 'RICL', 1).
synapse('ADAR', 'RIMR', 5).
synapse('ADAR', 'RIPR', 1).
synapse('ADAR', 'RIVR', 1).
synapse('ADAR', 'SMDVL', 2).
synapse('ADEL', 'ADAL', 1).
synapse('ADEL', 'ADER', 1).
synapse('ADEL', 'AINL', 1).
synapse('ADEL', 'AVAL', 2).
synapse('ADEL', 'AVAR', 3).
synapse('ADEL', 'AVEL', 1).
synapse('ADEL', 'AVKR', 1).
synapse('ADEL', 'AVL', 1).
synapse('ADEL', 'BDUL', 1).
synapse('ADEL', 'CEPDL', 1).
synapse('ADEL', 'FLPL', 1).
synapse('ADEL', 'FLPL', 1).
synapse('ADEL', 'IL1L', 1).
synapse('ADEL', 'IL2L', 1).
synapse('ADEL', 'IL2L', 1).
synapse('ADEL', 'OLLL', 1).
synapse('ADEL', 'OLLL', 1).
synapse('ADEL', 'RIAL', 1).
synapse('ADEL', 'RIFL', 1).
synapse('ADEL', 'RIGL', 2).
synapse('ADEL', 'RIGL', 3).
synapse('ADEL', 'RIGR', 3).
synapse('ADEL', 'RIGR', 3).
synapse('ADEL', 'RIH', 2).
synapse('ADEL', 'RIVL', 1).
synapse('ADEL', 'RIVR', 1).
synapse('ADEL', 'RMDL', 2).
synapse('ADEL', 'RMDL', 2).
synapse('ADEL', 'RMGL', 1).
synapse('ADEL', 'RMHL', 1).
synapse('ADEL', 'SIADR', 1).
synapse('ADEL', 'SIBDR', 1).
synapse('ADEL', 'SMBDR', 1).
synapse('ADEL', 'URBL', 1).
synapse('ADER', 'ADAR', 1).
synapse('ADER', 'ADEL', 2).
synapse('ADER', 'ALA', 1).
synapse('ADER', 'AVAL', 1).
synapse('ADER', 'AVAL', 4).
synapse('ADER', 'AVAR', 1).
synapse('ADER', 'AVDR', 2).
synapse('ADER', 'AVER', 1).
synapse('ADER', 'AVJR', 1).
synapse('ADER', 'AVKL', 1).
synapse('ADER', 'AVKL', 1).
synapse('ADER', 'AVKL', 1).
synapse('ADER', 'AVKR', 1).
synapse('ADER', 'CEPDR', 1).
synapse('ADER', 'FLPL', 1).
synapse('ADER', 'FLPR', 1).
synapse('ADER', 'OLLR', 2).
synapse('ADER', 'PVR', 1).
synapse('ADER', 'RIGL', 4).
synapse('ADER', 'RIGL', 3).
synapse('ADER', 'RIGR', 4).
synapse('ADER', 'RIH', 1).
synapse('ADER', 'RMDR', 2).
synapse('ADER', 'SAAVR', 1).
synapse('ADFL', 'ADAL', 1).
synapse('ADFL', 'ADAL', 1).
synapse('ADFL', 'AIZL', 5).
synapse('ADFL', 'AIZL', 7).
synapse('ADFL', 'AUAL', 1).
synapse('ADFL', 'AUAL', 4).
synapse('ADFL', 'OLQVL', 1).
synapse('ADFL', 'RIAL', 3).
synapse('ADFL', 'RIAL', 12).
synapse('ADFL', 'RIGL', 1).
synapse('ADFL', 'RIR', 2).
synapse('ADFL', 'SMBVL', 2).
synapse('ADFR', 'ADAR', 1).
synapse('ADFR', 'ADAR', 1).
synapse('ADFR', 'AIAR', 1).
synapse('ADFR', 'AIYR', 1).
synapse('ADFR', 'AIZR', 3).
synapse('ADFR', 'AIZR', 5).
synapse('ADFR', 'ASHR', 1).
synapse('ADFR', 'AUAR', 4).
synapse('ADFR', 'AWBR', 1).
synapse('ADFR', 'PVPR', 1).
synapse('ADFR', 'RIAR', 1).
synapse('ADFR', 'RIAR', 15).
synapse('ADFR', 'RIGR', 1).
synapse('ADFR', 'RIGR', 2).
synapse('ADFR', 'RIR', 3).
synapse('ADFR', 'SMBDR', 1).
synapse('ADFR', 'SMBVR', 2).
synapse('ADFR', 'URXR', 1).
synapse('ADLL', 'ADLR', 1).
synapse('ADLL', 'AIAL', 2).
synapse('ADLL', 'AIAL', 4).
synapse('ADLL', 'AIBL', 2).
synapse('ADLL', 'AIBL', 5).
synapse('ADLL', 'AIBR', 1).
synapse('ADLL', 'ALA', 2).
synapse('ADLL', 'ASER', 1).
synapse('ADLL', 'ASER', 2).
synapse('ADLL', 'ASHL', 2).
synapse('ADLL', 'AVAL', 2).
synapse('ADLL', 'AVAR', 3).
synapse('ADLL', 'AVBL', 2).
synapse('ADLL', 'AVBL', 2).
synapse('ADLL', 'AVDL', 1).
synapse('ADLL', 'AVDR', 4).
synapse('ADLL', 'AVDR', 1).
synapse('ADLL', 'AVJL', 1).
synapse('ADLL', 'AVJR', 3).
synapse('ADLL', 'AWBL', 2).
synapse('ADLL', 'OLQVL', 1).
synapse('ADLL', 'OLQVL', 1).
synapse('ADLL', 'RIPL', 1).
synapse('ADLL', 'RMGL', 1).
synapse('ADLR', 'ADLL', 1).
synapse('ADLR', 'AIAR', 2).
synapse('ADLR', 'AIAR', 8).
synapse('ADLR', 'AIBR', 10).
synapse('ADLR', 'ASER', 1).
synapse('ADLR', 'ASHR', 1).
synapse('ADLR', 'ASHR', 2).
synapse('ADLR', 'AVAR', 2).
synapse('ADLR', 'AVBL', 1).
synapse('ADLR', 'AVBR', 2).
synapse('ADLR', 'AVDL', 1).
synapse('ADLR', 'AVDL', 4).
synapse('ADLR', 'AVDR', 2).
synapse('ADLR', 'AVJR', 1).
synapse('ADLR', 'AVJR', 1).
synapse('ADLR', 'AWCR', 3).
synapse('ADLR', 'OLLR', 1).
synapse('ADLR', 'PVCL', 1).
synapse('ADLR', 'PVCL', 1).
synapse('ADLR', 'RICL', 1).
synapse('ADLR', 'RICR', 1).
synapse('AFDL', 'AFDR', 1).
synapse('AFDL', 'AIBL', 1).
synapse('AFDL', 'AINR', 1).
synapse('AFDL', 'AIYL', 7).
synapse('AFDR', 'AFDL', 1).
synapse('AFDR', 'AIBR', 1).
synapse('AFDR', 'AIYR', 12).
synapse('AFDR', 'AIYR', 1).
synapse('AFDR', 'ASER', 1).
synapse('AIAL', 'ADAL', 1).
synapse('AIAL', 'AIAR', 1).
synapse('AIAL', 'AIBL', 3).
synapse('AIAL', 'AIBL', 7).
synapse('AIAL', 'AIML', 2).
synapse('AIAL', 'AIZL', 1).
synapse('AIAL', 'ASER', 1).
synapse('AIAL', 'ASER', 2).
synapse('AIAL', 'ASGL', 1).
synapse('AIAL', 'ASHL', 1).
synapse('AIAL', 'ASIL', 2).
synapse('AIAL', 'ASKL', 2).
synapse('AIAL', 'ASKL', 1).
synapse('AIAL', 'AWAL', 1).
synapse('AIAL', 'AWCR', 1).
synapse('AIAL', 'HSNL', 1).
synapse('AIAL', 'RIFL', 1).
synapse('AIAL', 'RMGL', 1).
synapse('AIAR', 'ADAR', 1).
synapse('AIAR', 'ADFR', 1).
synapse('AIAR', 'ADLR', 2).
synapse('AIAR', 'AIAL', 1).
synapse('AIAR', 'AIBR', 6).
synapse('AIAR', 'AIBR', 8).
synapse('AIAR', 'AIZR', 1).
synapse('AIAR', 'ASER', 1).
synapse('AIAR', 'ASGR', 1).
synapse('AIAR', 'ASGR', 1).
synapse('AIAR', 'ASIR', 2).
synapse('AIAR', 'AWAR', 1).
synapse('AIAR', 'AWAR', 1).
synapse('AIAR', 'AWCL', 1).
synapse('AIAR', 'AWCR', 1).
synapse('AIAR', 'AWCR', 2).
synapse('AIAR', 'RIFR', 2).
synapse('AIBL', 'AFDL', 1).
synapse('AIBL', 'AIYL', 1).
synapse('AIBL', 'ASER', 1).
synapse('AIBL', 'AVAL', 2).
synapse('AIBL', 'AVBL', 1).
synapse('AIBL', 'AVBL', 4).
synapse('AIBL', 'DVC', 1).
synapse('AIBL', 'FLPL', 1).
synapse('AIBL', 'PVT', 1).
synapse('AIBL', 'RIBR', 1).
synapse('AIBL', 'RIBR', 3).
synapse('AIBL', 'RIFL', 1).
synapse('AIBL', 'RIGR', 1).
synapse('AIBL', 'RIGR', 3).
synapse('AIBL', 'RIML', 2).
synapse('AIBL', 'RIMR', 1).
synapse('AIBL', 'RIMR', 12).
synapse('AIBL', 'RIMR', 1).
synapse('AIBL', 'RIVL', 1).
synapse('AIBL', 'SAADL', 2).
synapse('AIBL', 'SAADR', 2).
synapse('AIBL', 'SMDDR', 4).
synapse('AIBR', 'AFDR', 1).
synapse('AIBR', 'AVAR', 1).
synapse('AIBR', 'AVBR', 3).
synapse('AIBR', 'AVEL', 1).
synapse('AIBR', 'DB1', 1).
synapse('AIBR', 'DVC', 2).
synapse('AIBR', 'PVT', 1).
synapse('AIBR', 'RIAL', 1).
synapse('AIBR', 'RIBL', 4).
synapse('AIBR', 'RIGL', 3).
synapse('AIBR', 'RIML', 4).
synapse('AIBR', 'RIML', 12).
synapse('AIBR', 'RIML', 1).
synapse('AIBR', 'RIMR', 1).
synapse('AIBR', 'RIS', 1).
synapse('AIBR', 'RIVR', 1).
synapse('AIBR', 'SAADL', 1).
synapse('AIBR', 'SMDDL', 1).
synapse('AIBR', 'SMDDL', 2).
synapse('AIBR', 'SMDVL', 1).
synapse('AIBR', 'VB1', 3).
synapse('AIML', 'AIAL', 1).
synapse('AIML', 'AIAL', 4).
synapse('AIML', 'ALML', 1).
synapse('AIML', 'ASGL', 2).
synapse('AIML', 'ASKL', 2).
synapse('AIML', 'AVBR', 2).
synapse('AIML', 'AVDL', 1).
synapse('AIML', 'AVDR', 1).
synapse('AIML', 'AVER', 1).
synapse('AIML', 'AVFL', 1).
synapse('AIML', 'AVFL', 3).
synapse('AIML', 'AVFR', 1).
synapse('AIML', 'AVHL', 2).
synapse('AIML', 'AVHR', 1).
synapse('AIML', 'AVJL', 1).
synapse('AIML', 'PVQL', 1).
synapse('AIML', 'RIFL', 1).
synapse('AIML', 'SIBDR', 1).
synapse('AIML', 'SMBVL', 1).
synapse('AIMR', 'AIAR', 5).
synapse('AIMR', 'ASGR', 2).
synapse('AIMR', 'ASJR', 2).
synapse('AIMR', 'ASKR', 3).
synapse('AIMR', 'AVDR', 1).
synapse('AIMR', 'AVFL', 1).
synapse('AIMR', 'AVFL', 1).
synapse('AIMR', 'AVFR', 1).
synapse('AIMR', 'AVFR', 1).
synapse('AIMR', 'HSNL', 1).
synapse('AIMR', 'HSNR', 2).
synapse('AIMR', 'OLQDR', 1).
synapse('AIMR', 'PVNR', 1).
synapse('AIMR', 'RIFR', 1).
synapse('AIMR', 'RMGR', 1).
synapse('AIMR', 'RMGR', 1).
synapse('AINL', 'ADEL', 1).
synapse('AINL', 'AFDR', 2).
synapse('AINL', 'AFDR', 3).
synapse('AINL', 'AINR', 2).
synapse('AINL', 'ASEL', 1).
synapse('AINL', 'ASEL', 2).
synapse('AINL', 'ASGR', 1).
synapse('AINL', 'ASGR', 1).
synapse('AINL', 'AUAR', 1).
synapse('AINL', 'AUAR', 1).
synapse('AINL', 'BAGL', 3).
synapse('AINL', 'RIBL', 1).
synapse('AINL', 'RIBR', 2).
synapse('AINR', 'AFDL', 3).
synapse('AINR', 'AFDL', 1).
synapse('AINR', 'AFDR', 1).
synapse('AINR', 'AIAL', 2).
synapse('AINR', 'AIBL', 2).
synapse('AINR', 'AINL', 2).
synapse('AINR', 'ASEL', 1).
synapse('AINR', 'ASER', 1).
synapse('AINR', 'ASER', 1).
synapse('AINR', 'ASGL', 1).
synapse('AINR', 'AUAL', 1).
synapse('AINR', 'AUAR', 1).
synapse('AINR', 'BAGR', 3).
synapse('AINR', 'RIBL', 2).
synapse('AINR', 'RID', 1).
synapse('AIYL', 'AIYR', 1).
synapse('AIYL', 'AIZL', 3).
synapse('AIYL', 'AIZL', 10).
synapse('AIYL', 'AWAL', 3).
synapse('AIYL', 'AWCL', 1).
synapse('AIYL', 'AWCR', 1).
synapse('AIYL', 'HSNR', 1).
synapse('AIYL', 'RIAL', 1).
synapse('AIYL', 'RIAL', 6).
synapse('AIYL', 'RIBL', 4).
synapse('AIYL', 'RIML', 1).
synapse('AIYR', 'ADFR', 1).
synapse('AIYR', 'AIYL', 1).
synapse('AIYR', 'AIZR', 8).
synapse('AIYR', 'AWAR', 1).
synapse('AIYR', 'HSNL', 1).
synapse('AIYR', 'RIAR', 6).
synapse('AIYR', 'RIBR', 2).
synapse('AIYR', 'RIMR', 1).
synapse('AIZL', 'AIAL', 3).
synapse('AIZL', 'AIBL', 2).
synapse('AIZL', 'AIBL', 2).
synapse('AIZL', 'AIBR', 2).
synapse('AIZL', 'AIBR', 6).
synapse('AIZL', 'AIZR', 2).
synapse('AIZL', 'ASEL', 1).
synapse('AIZL', 'ASGL', 1).
synapse('AIZL', 'ASHL', 1).
synapse('AIZL', 'AVER', 5).
synapse('AIZL', 'DVA', 1).
synapse('AIZL', 'RIAL', 3).
synapse('AIZL', 'RIAL', 5).
synapse('AIZL', 'RIGL', 1).
synapse('AIZL', 'RIML', 4).
synapse('AIZL', 'SMBDL', 1).
synapse('AIZL', 'SMBDL', 8).
synapse('AIZL', 'SMBVL', 7).
synapse('AIZL', 'VB2', 1).
synapse('AIZR', 'AIAR', 1).
synapse('AIZR', 'AIBL', 1).
synapse('AIZR', 'AIBL', 7).
synapse('AIZR', 'AIBR', 1).
synapse('AIZR', 'AIZL', 2).
synapse('AIZR', 'ASGR', 1).
synapse('AIZR', 'ASHR', 1).
synapse('AIZR', 'AVEL', 4).
synapse('AIZR', 'AVER', 1).
synapse('AIZR', 'AVER', 1).
synapse('AIZR', 'AWAR', 1).
synapse('AIZR', 'DVA', 1).
synapse('AIZR', 'DVA', 1).
synapse('AIZR', 'RIAR', 4).
synapse('AIZR', 'RIAR', 3).
synapse('AIZR', 'RIMR', 1).
synapse('AIZR', 'RIMR', 3).
synapse('AIZR', 'SMBDR', 5).
synapse('AIZR', 'SMBVR', 3).
synapse('AIZR', 'SMDDR', 1).
synapse('ALA', 'ADEL', 1).
synapse('ALA', 'AVAL', 1).
synapse('ALA', 'AVEL', 2).
synapse('ALA', 'AVER', 1).
synapse('ALA', 'AVER', 1).
synapse('ALA', 'RID', 1).
synapse('ALA', 'RMDR', 1).
synapse('ALML', 'AVDR', 1).
synapse('ALML', 'AVEL', 1).
synapse('ALML', 'AVM', 1).
synapse('ALML', 'BDUL', 5).
synapse('ALML', 'BDUL', 1).
synapse('ALML', 'CEPDL', 3).
synapse('ALML', 'CEPVL', 2).
synapse('ALML', 'PVCL', 2).
synapse('ALML', 'PVCL', 2).
synapse('ALML', 'PVCR', 1).
synapse('ALML', 'PVCR', 1).
synapse('ALML', 'PVR', 1).
synapse('ALML', 'RMDDR', 1).
synapse('ALML', 'RMGL', 1).
synapse('ALML', 'SDQL', 1).
synapse('ALMR', 'AVM', 1).
synapse('ALMR', 'BDUR', 5).
synapse('ALMR', 'CEPDR', 1).
synapse('ALMR', 'CEPVR', 1).
synapse('ALMR', 'PVCR', 3).
synapse('ALMR', 'RMDDL', 1).
synapse('ALMR', 'SIADL', 1).
synapse('ALNL', 'SAAVL', 3).
synapse('ALNL', 'SMBDR', 2).
synapse('ALNL', 'SMBDR', 1).
synapse('ALNL', 'SMDVL', 1).
synapse('ALNR', 'ADER', 1).
synapse('ALNR', 'RMHR', 1).
synapse('ALNR', 'SAAVR', 2).
synapse('ALNR', 'SMBDL', 2).
synapse('ALNR', 'SMDDR', 1).
synapse('ALNR', 'SMDVL', 1).
synapse('AQR', 'AVAL', 1).
synapse('AQR', 'AVAL', 1).
synapse('AQR', 'AVAR', 1).
synapse('AQR', 'AVAR', 2).
synapse('AQR', 'AVBL', 1).
synapse('AQR', 'AVBL', 2).
synapse('AQR', 'AVBL', 1).
synapse('AQR', 'AVBR', 4).
synapse('AQR', 'AVDL', 1).
synapse('AQR', 'AVDR', 1).
synapse('AQR', 'AVJL', 1).
synapse('AQR', 'AVKL', 2).
synapse('AQR', 'AVKR', 1).
synapse('AQR', 'BAGL', 2).
synapse('AQR', 'BAGR', 2).
synapse('AQR', 'PVCR', 2).
synapse('AQR', 'PVPL', 1).
synapse('AQR', 'PVPL', 7).
synapse('AQR', 'PVPR', 9).
synapse('AQR', 'RIAL', 1).
synapse('AQR', 'RIAL', 2).
synapse('AQR', 'RIAR', 1).
synapse('AQR', 'RIAR', 1).
synapse('AQR', 'RIGL', 2).
synapse('AQR', 'RIGR', 1).
synapse('AQR', 'URXL', 1).
synapse('AS1', 'AVAL', 3).
synapse('AS1', 'AVAR', 2).
synapse('AS1', 'DA1', 2).
synapse('AS1', 'MUS', 13).
synapse('AS1', 'VA3', 1).
synapse('AS1', 'VD1', 5).
synapse('AS1', 'VD2', 1).
synapse('AS2', 'DA2', 1).
synapse('AS2', 'DB1', 1).
synapse('AS2', 'DD1', 1).
synapse('AS2', 'MUS', 11).
synapse('AS2', 'VA4', 2).
synapse('AS2', 'VD2', 10).
synapse('AS3', 'AVAL', 2).
synapse('AS3', 'AVAR', 1).
synapse('AS3', 'DA2', 1).
synapse('AS3', 'DA3', 1).
synapse('AS3', 'DD1', 1).
synapse('AS3', 'MUS', 12).
synapse('AS3', 'VA5', 2).
synapse('AS3', 'VD2', 1).
synapse('AS3', 'VD3', 15).
synapse('AS4', 'AS5', 1).
synapse('AS4', 'DA3', 1).
synapse('AS4', 'MUS', 9).
synapse('AS4', 'VD4', 11).
synapse('AS5', 'AVAL', 1).
synapse('AS5', 'AVAR', 1).
synapse('AS5', 'DD2', 1).
synapse('AS5', 'MUS', 10).
synapse('AS5', 'VA7', 1).
synapse('AS5', 'VD5', 9).
synapse('AS6', 'AVAL', 1).
synapse('AS6', 'AVAR', 1).
synapse('AS6', 'AVBR', 1).
synapse('AS6', 'DA5', 2).
synapse('AS6', 'MUS', 10).
synapse('AS6', 'VA8', 1).
synapse('AS6', 'VD6', 13).
synapse('AS7', 'AVAL', 6).
synapse('AS7', 'AVAR', 5).
synapse('AS7', 'AVBL', 2).
synapse('AS7', 'AVBR', 2).
synapse('AS8', 'AVAL', 4).
synapse('AS8', 'AVAR', 3).
synapse('AS9', 'AVAL', 4).
synapse('AS9', 'AVAR', 1).
synapse('AS9', 'AVAR', 1).
synapse('AS9', 'DVB', 7).
synapse('AS9', 'MUS', 1).
synapse('AS10', 'AVAL', 1).
synapse('AS10', 'AVAR', 1).
synapse('AS11', 'MUS', 2).
synapse('AS11', 'PDA', 1).
synapse('AS11', 'PDB', 1).
synapse('AS11', 'PDB', 2).
synapse('AS11', 'VD13', 2).
synapse('ASEL', 'ADFR', 1).
synapse('ASEL', 'AIAL', 3).
synapse('ASEL', 'AIBL', 1).
synapse('ASEL', 'AIBL', 6).
synapse('ASEL', 'AIBR', 2).
synapse('ASEL', 'AIBR', 2).
synapse('ASEL', 'AIYL', 8).
synapse('ASEL', 'AIYL', 5).
synapse('ASEL', 'AIYR', 5).
synapse('ASEL', 'AIYR', 1).
synapse('ASEL', 'AWCL', 4).
synapse('ASEL', 'AWCR', 1).
synapse('ASEL', 'RIAR', 1).
synapse('ASER', 'AFDL', 1).
synapse('ASER', 'AFDL', 1).
synapse('ASER', 'AFDR', 2).
synapse('ASER', 'AIAL', 1).
synapse('ASER', 'AIAL', 1).
synapse('ASER', 'AIAR', 1).
synapse('ASER', 'AIAR', 2).
synapse('ASER', 'AIBL', 2).
synapse('ASER', 'AIBR', 1).
synapse('ASER', 'AIBR', 9).
synapse('ASER', 'AIYL', 2).
synapse('ASER', 'AIYL', 2).
synapse('ASER', 'AIYR', 4).
synapse('ASER', 'AIYR', 10).
synapse('ASER', 'AWAR', 1).
synapse('ASER', 'AWCL', 1).
synapse('ASER', 'AWCR', 1).
synapse('ASGL', 'AIAL', 6).
synapse('ASGL', 'AIAL', 3).
synapse('ASGL', 'AIBL', 3).
synapse('ASGL', 'AINR', 1).
synapse('ASGL', 'AINR', 1).
synapse('ASGL', 'AIZL', 1).
synapse('ASGL', 'ASKL', 1).
synapse('ASGR', 'AIAR', 8).
synapse('ASGR', 'AIAR', 2).
synapse('ASGR', 'AIBR', 2).
synapse('ASGR', 'AINL', 1).
synapse('ASGR', 'AIYR', 1).
synapse('ASGR', 'AIZR', 1).
synapse('ASHL', 'ADAL', 1).
synapse('ASHL', 'ADAL', 1).
synapse('ASHL', 'ADFL', 3).
synapse('ASHL', 'AIAL', 5).
synapse('ASHL', 'AIAL', 2).
synapse('ASHL', 'AIBL', 2).
synapse('ASHL', 'AIBL', 3).
synapse('ASHL', 'AIZL', 1).
synapse('ASHL', 'ASHR', 1).
synapse('ASHL', 'ASKL', 1).
synapse('ASHL', 'AVAL', 2).
synapse('ASHL', 'AVBL', 6).
synapse('ASHL', 'AVDL', 2).
synapse('ASHL', 'AVDR', 2).
synapse('ASHL', 'AVDR', 2).
synapse('ASHL', 'RIAL', 4).
synapse('ASHL', 'RICL', 2).
synapse('ASHL', 'RIML', 1).
synapse('ASHL', 'RIPL', 1).
synapse('ASHL', 'RMGL', 1).
synapse('ASHR', 'ADAR', 1).
synapse('ASHR', 'ADAR', 2).
synapse('ASHR', 'ADFR', 2).
synapse('ASHR', 'AIAR', 6).
synapse('ASHR', 'AIAR', 4).
synapse('ASHR', 'AIBR', 1).
synapse('ASHR', 'AIBR', 2).
synapse('ASHR', 'AIZR', 1).
synapse('ASHR', 'ASHL', 1).
synapse('ASHR', 'ASKR', 1).
synapse('ASHR', 'AVAR', 1).
synapse('ASHR', 'AVAR', 4).
synapse('ASHR', 'AVBR', 3).
synapse('ASHR', 'AVDL', 1).
synapse('ASHR', 'AVDL', 4).
synapse('ASHR', 'AVDR', 1).
synapse('ASHR', 'AVER', 3).
synapse('ASHR', 'HSNR', 1).
synapse('ASHR', 'PVPR', 1).
synapse('ASHR', 'RIAR', 2).
synapse('ASHR', 'RICR', 2).
synapse('ASHR', 'RMGR', 2).
synapse('ASHR', 'RMGR', 1).
synapse('ASIL', 'AIAL', 2).
synapse('ASIL', 'AIBL', 1).
synapse('ASIL', 'AIYL', 2).
synapse('ASIL', 'AIZL', 1).
synapse('ASIL', 'ASER', 1).
synapse('ASIL', 'ASIR', 1).
synapse('ASIL', 'ASKL', 2).
synapse('ASIL', 'AWCL', 1).
synapse('ASIL', 'AWCL', 1).
synapse('ASIL', 'AWCR', 1).
synapse('ASIL', 'AWCR', 1).
synapse('ASIL', 'RIBL', 1).
synapse('ASIR', 'AIAL', 1).
synapse('ASIR', 'AIAR', 2).
synapse('ASIR', 'AIAR', 1).
synapse('ASIR', 'AIAR', 2).
synapse('ASIR', 'AIBR', 1).
synapse('ASIR', 'ASEL', 2).
synapse('ASIR', 'ASHR', 1).
synapse('ASIR', 'ASIL', 1).
synapse('ASIR', 'AWCL', 1).
synapse('ASIR', 'AWCR', 1).
synapse('ASIR', 'AWCR', 1).
synapse('ASJL', 'ASJR', 1).
synapse('ASJL', 'ASKL', 4).
synapse('ASJL', 'HSNL', 1).
synapse('ASJL', 'HSNR', 1).
synapse('ASJL', 'PVQL', 8).
synapse('ASJL', 'PVQL', 6).
synapse('ASJR', 'ASJL', 1).
synapse('ASJR', 'ASKR', 1).
synapse('ASJR', 'ASKR', 3).
synapse('ASJR', 'HSNR', 1).
synapse('ASJR', 'PVQR', 9).
synapse('ASJR', 'PVQR', 4).
synapse('ASKL', 'AIAL', 7).
synapse('ASKL', 'AIAL', 4).
synapse('ASKL', 'AIBL', 2).
synapse('ASKL', 'AIML', 2).
synapse('ASKL', 'ASKR', 1).
synapse('ASKL', 'PVQL', 5).
synapse('ASKL', 'RMGL', 1).
synapse('ASKR', 'AIAR', 8).
synapse('ASKR', 'AIAR', 3).
synapse('ASKR', 'AIMR', 1).
synapse('ASKR', 'ASHR', 1).
synapse('ASKR', 'ASKL', 1).
synapse('ASKR', 'AWAR', 1).
synapse('ASKR', 'CEPVR', 1).
synapse('ASKR', 'PVQR', 4).
synapse('ASKR', 'RIFR', 1).
synapse('ASKR', 'RMGR', 1).
synapse('AUAL', 'AINR', 1).
synapse('AUAL', 'AUAR', 1).
synapse('AUAL', 'AVAL', 1).
synapse('AUAL', 'AVAL', 2).
synapse('AUAL', 'AVDR', 1).
synapse('AUAL', 'AVEL', 3).
synapse('AUAL', 'AWBL', 1).
synapse('AUAL', 'RIAL', 5).
synapse('AUAL', 'RIBL', 2).
synapse('AUAL', 'RIBL', 7).
synapse('AUAR', 'AINL', 1).
synapse('AUAR', 'AIYR', 1).
synapse('AUAR', 'AUAL', 1).
synapse('AUAR', 'AVAR', 1).
synapse('AUAR', 'AVER', 1).
synapse('AUAR', 'AVER', 3).
synapse('AUAR', 'AWBR', 1).
synapse('AUAR', 'RIAR', 1).
synapse('AUAR', 'RIAR', 5).
synapse('AUAR', 'RIBR', 4).
synapse('AUAR', 'RIBR', 9).
synapse('AUAR', 'URXR', 1).
synapse('AVAL', 'AS1', 3).
synapse('AVAL', 'AS2', 1).
synapse('AVAL', 'AS3', 2).
synapse('AVAL', 'AS3', 1).
synapse('AVAL', 'AS4', 1).
synapse('AVAL', 'AS5', 1).
synapse('AVAL', 'AS5', 3).
synapse('AVAL', 'AS6', 1).
synapse('AVAL', 'AS7', 6).
synapse('AVAL', 'AS7', 8).
synapse('AVAL', 'AS8', 4).
synapse('AVAL', 'AS8', 5).
synapse('AVAL', 'AS9', 4).
synapse('AVAL', 'AS9', 8).
synapse('AVAL', 'AS10', 1).
synapse('AVAL', 'AS10', 2).
synapse('AVAL', 'AS11', 4).
synapse('AVAL', 'AVAR', 2).
synapse('AVAL', 'AVAR', 5).
synapse('AVAL', 'AVBR', 1).
synapse('AVAL', 'AVDL', 1).
synapse('AVAL', 'AVHL', 1).
synapse('AVAL', 'AVJL', 2).
synapse('AVAL', 'DA1', 2).
synapse('AVAL', 'DA1', 2).
synapse('AVAL', 'DA2', 2).
synapse('AVAL', 'DA2', 2).
synapse('AVAL', 'DA3', 6).
synapse('AVAL', 'DA4', 7).
synapse('AVAL', 'DA4', 3).
synapse('AVAL', 'DA5', 7).
synapse('AVAL', 'DA5', 1).
synapse('AVAL', 'DA6', 11).
synapse('AVAL', 'DA6', 10).
synapse('AVAL', 'DA7', 2).
synapse('AVAL', 'DA7', 2).
synapse('AVAL', 'DA8', 4).
synapse('AVAL', 'DA9', 2).
synapse('AVAL', 'DA9', 1).
synapse('AVAL', 'DB5', 2).
synapse('AVAL', 'DB6', 1).
synapse('AVAL', 'DB6', 3).
synapse('AVAL', 'FLPL', 1).
synapse('AVAL', 'LUAL', 1).
synapse('AVAL', 'LUAL', 1).
synapse('AVAL', 'PVCL', 3).
synapse('AVAL', 'PVCL', 7).
synapse('AVAL', 'PVCL', 2).
synapse('AVAL', 'PVCR', 2).
synapse('AVAL', 'PVCR', 4).
synapse('AVAL', 'PVCR', 5).
synapse('AVAL', 'PVPL', 1).
synapse('AVAL', 'RIMR', 3).
synapse('AVAL', 'SABD', 4).
synapse('AVAL', 'SABVR', 1).
synapse('AVAL', 'SDQR', 1).
synapse('AVAL', 'URYDL', 1).
synapse('AVAL', 'URYVR', 1).
synapse('AVAL', 'VA1', 3).
synapse('AVAL', 'VA2', 1).
synapse('AVAL', 'VA2', 4).
synapse('AVAL', 'VA3', 2).
synapse('AVAL', 'VA3', 1).
synapse('AVAL', 'VA4', 2).
synapse('AVAL', 'VA4', 1).
synapse('AVAL', 'VA5', 3).
synapse('AVAL', 'VA5', 5).
synapse('AVAL', 'VA6', 4).
synapse('AVAL', 'VA6', 6).
synapse('AVAL', 'VA7', 2).
synapse('AVAL', 'VA8', 9).
synapse('AVAL', 'VA8', 10).
synapse('AVAL', 'VA9', 7).
synapse('AVAL', 'VA9', 1).
synapse('AVAL', 'VA10', 5).
synapse('AVAL', 'VA10', 1).
synapse('AVAL', 'VA11', 6).
synapse('AVAL', 'VA11', 1).
synapse('AVAL', 'VA12', 2).
synapse('AVAL', 'VB9', 5).
synapse('AVAR', 'ADER', 1).
synapse('AVAR', 'AS1', 2).
synapse('AVAR', 'AS1', 1).
synapse('AVAR', 'AS2', 2).
synapse('AVAR', 'AS3', 1).
synapse('AVAR', 'AS3', 1).
synapse('AVAR', 'AS4', 1).
synapse('AVAR', 'AS5', 1).
synapse('AVAR', 'AS5', 1).
synapse('AVAR', 'AS6', 1).
synapse('AVAR', 'AS6', 2).
synapse('AVAR', 'AS7', 5).
synapse('AVAR', 'AS7', 3).
synapse('AVAR', 'AS8', 3).
synapse('AVAR', 'AS8', 6).
synapse('AVAR', 'AS9', 1).
synapse('AVAR', 'AS9', 5).
synapse('AVAR', 'AS10', 1).
synapse('AVAR', 'AS10', 1).
synapse('AVAR', 'AS11', 6).
synapse('AVAR', 'AVAL', 5).
synapse('AVAR', 'AVAL', 1).
synapse('AVAR', 'AVBL', 1).
synapse('AVAR', 'AVDL', 1).
synapse('AVAR', 'AVDR', 2).
synapse('AVAR', 'AVEL', 2).
synapse('AVAR', 'AVER', 2).
synapse('AVAR', 'DA1', 2).
synapse('AVAR', 'DA1', 6).
synapse('AVAR', 'DA2', 2).
synapse('AVAR', 'DA2', 2).
synapse('AVAR', 'DA3', 3).
synapse('AVAR', 'DA3', 2).
synapse('AVAR', 'DA4', 6).
synapse('AVAR', 'DA4', 2).
synapse('AVAR', 'DA5', 2).
synapse('AVAR', 'DA5', 5).
synapse('AVAR', 'DA6', 11).
synapse('AVAR', 'DA6', 2).
synapse('AVAR', 'DA7', 3).
synapse('AVAR', 'DA8', 1).
synapse('AVAR', 'DA8', 7).
synapse('AVAR', 'DA8', 1).
synapse('AVAR', 'DA9', 2).
synapse('AVAR', 'DB3', 1).
synapse('AVAR', 'DB5', 1).
synapse('AVAR', 'DB5', 2).
synapse('AVAR', 'DB6', 5).
synapse('AVAR', 'LUAL', 1).
synapse('AVAR', 'LUAR', 3).
synapse('AVAR', 'PDEL', 1).
synapse('AVAR', 'PDER', 1).
synapse('AVAR', 'PVCL', 2).
synapse('AVAR', 'PVCL', 5).
synapse('AVAR', 'PVCR', 5).
synapse('AVAR', 'PVCR', 3).
synapse('AVAR', 'RIGL', 1).
synapse('AVAR', 'RIML', 2).
synapse('AVAR', 'RIMR', 1).
synapse('AVAR', 'SABD', 1).
synapse('AVAR', 'SABVL', 1).
synapse('AVAR', 'SABVL', 2).
synapse('AVAR', 'SABVL', 3).
synapse('AVAR', 'SABVR', 1).
synapse('AVAR', 'URYDR', 1).
synapse('AVAR', 'URYVL', 1).
synapse('AVAR', 'VA2', 2).
synapse('AVAR', 'VA3', 5).
synapse('AVAR', 'VA3', 2).
synapse('AVAR', 'VA4', 2).
synapse('AVAR', 'VA4', 3).
synapse('AVAR', 'VA5', 1).
synapse('AVAR', 'VA5', 3).
synapse('AVAR', 'VA6', 3).
synapse('AVAR', 'VA6', 2).
synapse('AVAR', 'VA7', 4).
synapse('AVAR', 'VA8', 11).
synapse('AVAR', 'VA8', 1).
synapse('AVAR', 'VA8', 4).
synapse('AVAR', 'VA9', 4).
synapse('AVAR', 'VA9', 2).
synapse('AVAR', 'VA10', 4).
synapse('AVAR', 'VA10', 1).
synapse('AVAR', 'VA11', 8).
synapse('AVAR', 'VA11', 7).
synapse('AVAR', 'VA12', 1).
synapse('AVAR', 'VB9', 4).
synapse('AVAR', 'VD13', 2).
synapse('AVBL', 'AQR', 1).
synapse('AVBL', 'AS3', 1).
synapse('AVBL', 'AS4', 1).
synapse('AVBL', 'AS5', 1).
synapse('AVBL', 'AS6', 1).
synapse('AVBL', 'AS7', 2).
synapse('AVBL', 'AS9', 1).
synapse('AVBL', 'AS10', 1).
synapse('AVBL', 'AVAL', 6).
synapse('AVBL', 'AVAL', 1).
synapse('AVBL', 'AVAR', 5).
synapse('AVBL', 'AVAR', 2).
synapse('AVBL', 'AVBR', 1).
synapse('AVBL', 'AVBR', 3).
synapse('AVBL', 'AVDL', 1).
synapse('AVBL', 'AVDR', 2).
synapse('AVBL', 'AVEL', 1).
synapse('AVBL', 'AVER', 2).
synapse('AVBL', 'AVL', 1).
synapse('AVBL', 'DB3', 1).
synapse('AVBL', 'DB4', 1).
synapse('AVBL', 'DB5', 1).
synapse('AVBL', 'DB6', 2).
synapse('AVBL', 'DB7', 2).
synapse('AVBL', 'DVA', 1).
synapse('AVBL', 'PVNR', 1).
synapse('AVBL', 'RIBL', 1).
synapse('AVBL', 'RIBR', 1).
synapse('AVBL', 'RID', 1).
synapse('AVBL', 'SDQR', 1).
synapse('AVBL', 'SIBVL', 1).
synapse('AVBL', 'VA2', 1).
synapse('AVBL', 'VA7', 1).
synapse('AVBL', 'VA10', 1).
synapse('AVBL', 'VB1', 1).
synapse('AVBL', 'VB2', 1).
synapse('AVBL', 'VB2', 3).
synapse('AVBL', 'VB4', 1).
synapse('AVBL', 'VB5', 1).
synapse('AVBL', 'VB6', 1).
synapse('AVBL', 'VB7', 2).
synapse('AVBL', 'VB8', 7).
synapse('AVBL', 'VB9', 1).
synapse('AVBL', 'VB10', 2).
synapse('AVBL', 'VB11', 2).
synapse('AVBL', 'VC3', 1).
synapse('AVBR', 'AS1', 1).
synapse('AVBR', 'AS3', 1).
synapse('AVBR', 'AS4', 1).
synapse('AVBR', 'AS5', 1).
synapse('AVBR', 'AS6', 1).
synapse('AVBR', 'AS6', 1).
synapse('AVBR', 'AS7', 2).
synapse('AVBR', 'AS7', 1).
synapse('AVBR', 'AS10', 1).
synapse('AVBR', 'AVAL', 5).
synapse('AVBR', 'AVAL', 1).
synapse('AVBR', 'AVAR', 5).
synapse('AVBR', 'AVAR', 2).
synapse('AVBR', 'AVBL', 3).
synapse('AVBR', 'AVBL', 1).
synapse('AVBR', 'DA5', 1).
synapse('AVBR', 'DB1', 3).
synapse('AVBR', 'DB2', 1).
synapse('AVBR', 'DB3', 1).
synapse('AVBR', 'DB4', 1).
synapse('AVBR', 'DB5', 1).
synapse('AVBR', 'DB6', 1).
synapse('AVBR', 'DB7', 1).
synapse('AVBR', 'DD1', 1).
synapse('AVBR', 'DVA', 1).
synapse('AVBR', 'HSNR', 1).
synapse('AVBR', 'PVNL', 2).
synapse('AVBR', 'RIBL', 1).
synapse('AVBR', 'RIBR', 1).
synapse('AVBR', 'RID', 2).
synapse('AVBR', 'SIBVL', 1).
synapse('AVBR', 'VA4', 1).
synapse('AVBR', 'VA8', 1).
synapse('AVBR', 'VA9', 1).
synapse('AVBR', 'VA9', 1).
synapse('AVBR', 'VB2', 1).
synapse('AVBR', 'VB3', 1).
synapse('AVBR', 'VB4', 1).
synapse('AVBR', 'VB6', 2).
synapse('AVBR', 'VB7', 2).
synapse('AVBR', 'VB8', 3).
synapse('AVBR', 'VB9', 6).
synapse('AVBR', 'VB10', 1).
synapse('AVBR', 'VB11', 1).
synapse('AVBR', 'VD3', 1).
synapse('AVBR', 'VD10', 1).
synapse('AVDL', 'ADAR', 2).
synapse('AVDL', 'AS1', 1).
synapse('AVDL', 'AS4', 1).
synapse('AVDL', 'AS5', 1).
synapse('AVDL', 'AS10', 1).
synapse('AVDL', 'AS11', 2).
synapse('AVDL', 'AVAL', 1).
synapse('AVDL', 'AVAL', 12).
synapse('AVDL', 'AVAR', 2).
synapse('AVDL', 'AVAR', 17).
synapse('AVDL', 'AVM', 2).
synapse('AVDL', 'DA1', 1).
synapse('AVDL', 'DA2', 1).
synapse('AVDL', 'DA3', 4).
synapse('AVDL', 'DA4', 1).
synapse('AVDL', 'DA4', 1).
synapse('AVDL', 'DA5', 1).
synapse('AVDL', 'DA8', 1).
synapse('AVDL', 'FLPL', 1).
synapse('AVDL', 'FLPR', 1).
synapse('AVDL', 'LUAL', 1).
synapse('AVDL', 'PVCL', 1).
synapse('AVDL', 'SABD', 1).
synapse('AVDL', 'SABD', 1).
synapse('AVDL', 'SABVL', 1).
synapse('AVDL', 'SABVR', 1).
synapse('AVDL', 'VA5', 1).
synapse('AVDL', 'VA5', 1).
synapse('AVDR', 'ADAL', 2).
synapse('AVDR', 'ADLL', 1).
synapse('AVDR', 'AS5', 1).
synapse('AVDR', 'AS10', 1).
synapse('AVDR', 'AVAL', 3).
synapse('AVDR', 'AVAL', 13).
synapse('AVDR', 'AVAR', 1).
synapse('AVDR', 'AVAR', 14).
synapse('AVDR', 'AVBL', 1).
synapse('AVDR', 'AVDL', 2).
synapse('AVDR', 'AVJL', 2).
synapse('AVDR', 'DA1', 2).
synapse('AVDR', 'DA2', 1).
synapse('AVDR', 'DA3', 1).
synapse('AVDR', 'DA3', 1).
synapse('AVDR', 'DA4', 1).
synapse('AVDR', 'DA4', 1).
synapse('AVDR', 'DA5', 2).
synapse('AVDR', 'DA8', 1).
synapse('AVDR', 'DA9', 1).
synapse('AVDR', 'DB4', 1).
synapse('AVDR', 'DVC', 1).
synapse('AVDR', 'FLPR', 1).
synapse('AVDR', 'LUAL', 2).
synapse('AVDR', 'PQR', 1).
synapse('AVDR', 'SABD', 1).
synapse('AVDR', 'SABVL', 3).
synapse('AVDR', 'SABVR', 1).
synapse('AVDR', 'VA2', 1).
synapse('AVDR', 'VA3', 2).
synapse('AVDR', 'VA6', 1).
synapse('AVDR', 'VA11', 1).
synapse('AVEL', 'AS1', 1).
synapse('AVEL', 'AVAL', 2).
synapse('AVEL', 'AVAL', 10).
synapse('AVEL', 'AVAR', 4).
synapse('AVEL', 'AVAR', 3).
synapse('AVEL', 'AVER', 1).
synapse('AVEL', 'DA1', 5).
synapse('AVEL', 'DA2', 1).
synapse('AVEL', 'DA3', 1).
synapse('AVEL', 'DA3', 2).
synapse('AVEL', 'DA4', 1).
synapse('AVEL', 'PVCR', 1).
synapse('AVEL', 'PVT', 1).
synapse('AVEL', 'RIML', 2).
synapse('AVEL', 'RIMR', 3).
synapse('AVEL', 'RMDVR', 1).
synapse('AVEL', 'RMEV', 1).
synapse('AVEL', 'SABD', 6).
synapse('AVEL', 'SABVL', 7).
synapse('AVEL', 'SABVR', 3).
synapse('AVEL', 'VA1', 5).
synapse('AVEL', 'VA3', 1).
synapse('AVEL', 'VA3', 2).
synapse('AVEL', 'VD2', 1).
synapse('AVEL', 'VD3', 1).
synapse('AVER', 'AS1', 1).
synapse('AVER', 'AS1', 2).
synapse('AVER', 'AS2', 2).
synapse('AVER', 'AS3', 1).
synapse('AVER', 'AVAL', 2).
synapse('AVER', 'AVAL', 5).
synapse('AVER', 'AVAR', 16).
synapse('AVER', 'AVDR', 1).
synapse('AVER', 'AVEL', 1).
synapse('AVER', 'DA1', 5).
synapse('AVER', 'DA2', 1).
synapse('AVER', 'DA2', 2).
synapse('AVER', 'DA3', 1).
synapse('AVER', 'DB3', 1).
synapse('AVER', 'RIML', 3).
synapse('AVER', 'RIMR', 2).
synapse('AVER', 'RMDVL', 1).
synapse('AVER', 'RMDVR', 1).
synapse('AVER', 'RMEV', 1).
synapse('AVER', 'SABD', 2).
synapse('AVER', 'SABVL', 3).
synapse('AVER', 'SABVR', 3).
synapse('AVER', 'VA1', 1).
synapse('AVER', 'VA2', 1).
synapse('AVER', 'VA3', 2).
synapse('AVER', 'VA4', 1).
synapse('AVER', 'VA5', 1).
synapse('AVFL', 'AVBL', 1).
synapse('AVFL', 'AVBR', 2).
synapse('AVFL', 'AVFR', 1).
synapse('AVFL', 'AVFR', 6).
synapse('AVFL', 'AVFR', 23).
synapse('AVFL', 'AVG', 1).
synapse('AVFL', 'AVG', 1).
synapse('AVFL', 'AVHL', 2).
synapse('AVFL', 'AVHL', 2).
synapse('AVFL', 'AVHR', 3).
synapse('AVFL', 'AVHR', 1).
synapse('AVFL', 'AVHR', 3).
synapse('AVFL', 'AVJL', 1).
synapse('AVFL', 'AVJR', 1).
synapse('AVFL', 'AVL', 1).
synapse('AVFL', 'HSNL', 1).
synapse('AVFL', 'MUS', 2).
synapse('AVFL', 'PDER', 1).
synapse('AVFL', 'PVNL', 2).
synapse('AVFL', 'PVQL', 1).
synapse('AVFL', 'PVQR', 1).
synapse('AVFL', 'PVQR', 1).
synapse('AVFL', 'VB1', 1).
synapse('AVFL', 'VB1', 0).
synapse('AVFR', 'ASJL', 1).
synapse('AVFR', 'ASKL', 1).
synapse('AVFR', 'AVBL', 1).
synapse('AVFR', 'AVBR', 3).
synapse('AVFR', 'AVBR', 2).
synapse('AVFR', 'AVFL', 23).
synapse('AVFR', 'AVFL', 1).
synapse('AVFR', 'AVHL', 2).
synapse('AVFR', 'AVHL', 2).
synapse('AVFR', 'AVHR', 1).
synapse('AVFR', 'AVHR', 1).
synapse('AVFR', 'AVJL', 1).
synapse('AVFR', 'AVJL', 1).
synapse('AVFR', 'AVJR', 1).
synapse('AVFR', 'HSNR', 1).
synapse('AVFR', 'MUS', 4).
synapse('AVFR', 'PVQL', 1).
synapse('AVFR', 'VC4', 1).
synapse('AVFR', 'VD11', 1).
synapse('AVG', 'AVAR', 1).
synapse('AVG', 'AVAR', 2).
synapse('AVG', 'AVBL', 1).
synapse('AVG', 'AVBL', 1).
synapse('AVG', 'AVBR', 2).
synapse('AVG', 'AVDR', 1).
synapse('AVG', 'AVEL', 1).
synapse('AVG', 'AVER', 1).
synapse('AVG', 'AVFL', 1).
synapse('AVG', 'AVJL', 1).
synapse('AVG', 'AVL', 1).
synapse('AVG', 'DA8', 1).
synapse('AVG', 'PHAL', 2).
synapse('AVG', 'PVCL', 1).
synapse('AVG', 'PVNR', 1).
synapse('AVG', 'PVNR', 1).
synapse('AVG', 'PVPR', 1).
synapse('AVG', 'PVQR', 1).
synapse('AVG', 'PVT', 1).
synapse('AVG', 'RIFL', 1).
synapse('AVG', 'RIFR', 1).
synapse('AVG', 'VA11', 1).
synapse('AVHL', 'ADFR', 3).
synapse('AVHL', 'AVBL', 1).
synapse('AVHL', 'AVBR', 1).
synapse('AVHL', 'AVDL', 1).
synapse('AVHL', 'AVFL', 2).
synapse('AVHL', 'AVFL', 1).
synapse('AVHL', 'AVFR', 2).
synapse('AVHL', 'AVFR', 3).
synapse('AVHL', 'AVHR', 1).
synapse('AVHL', 'AVHR', 1).
synapse('AVHL', 'AVJL', 2).
synapse('AVHL', 'AVJL', 1).
synapse('AVHL', 'AWBR', 1).
synapse('AVHL', 'PHBR', 1).
synapse('AVHL', 'PVPR', 2).
synapse('AVHL', 'PVQL', 1).
synapse('AVHL', 'PVQR', 2).
synapse('AVHL', 'RIMR', 1).
synapse('AVHL', 'RIR', 3).
synapse('AVHL', 'SMBDR', 1).
synapse('AVHL', 'SMBVR', 2).
synapse('AVHL', 'VD1', 1).
synapse('AVHR', 'ADLL', 1).
synapse('AVHR', 'ADLR', 2).
synapse('AVHR', 'AQR', 2).
synapse('AVHR', 'AVBL', 2).
synapse('AVHR', 'AVBR', 1).
synapse('AVHR', 'AVDR', 1).
synapse('AVHR', 'AVFL', 3).
synapse('AVHR', 'AVFL', 2).
synapse('AVHR', 'AVFR', 1).
synapse('AVHR', 'AVFR', 1).
synapse('AVHR', 'AVHL', 1).
synapse('AVHR', 'AVHL', 1).
synapse('AVHR', 'AVJR', 4).
synapse('AVHR', 'PVNL', 1).
synapse('AVHR', 'PVPL', 3).
synapse('AVHR', 'RIGL', 1).
synapse('AVHR', 'RIR', 1).
synapse('AVHR', 'RIR', 3).
synapse('AVHR', 'SMBDL', 1).
synapse('AVHR', 'SMBVL', 1).
synapse('AVJL', 'AVAL', 2).
synapse('AVJL', 'AVAR', 1).
synapse('AVJL', 'AVBL', 1).
synapse('AVJL', 'AVBR', 4).
synapse('AVJL', 'AVDL', 1).
synapse('AVJL', 'AVDR', 2).
synapse('AVJL', 'AVEL', 1).
synapse('AVJL', 'AVFR', 1).
synapse('AVJL', 'AVHL', 2).
synapse('AVJL', 'AVJR', 4).
synapse('AVJL', 'HSNR', 1).
synapse('AVJL', 'PLMR', 2).
synapse('AVJL', 'PVCL', 1).
synapse('AVJL', 'PVCL', 1).
synapse('AVJL', 'PVCR', 2).
synapse('AVJL', 'PVCR', 3).
synapse('AVJL', 'PVNR', 1).
synapse('AVJL', 'RIFR', 1).
synapse('AVJL', 'RIS', 1).
synapse('AVJL', 'RIS', 1).
synapse('AVJR', 'AVAL', 1).
synapse('AVJR', 'AVAR', 1).
synapse('AVJR', 'AVBL', 1).
synapse('AVJR', 'AVBL', 2).
synapse('AVJR', 'AVBR', 1).
synapse('AVJR', 'AVDL', 1).
synapse('AVJR', 'AVDR', 1).
synapse('AVJR', 'AVDR', 2).
synapse('AVJR', 'AVER', 1).
synapse('AVJR', 'AVER', 2).
synapse('AVJR', 'AVJL', 4).
synapse('AVJR', 'AVJL', 1).
synapse('AVJR', 'PVCL', 2).
synapse('AVJR', 'PVCL', 1).
synapse('AVJR', 'PVCR', 1).
synapse('AVJR', 'PVCR', 3).
synapse('AVJR', 'PVQR', 1).
synapse('AVJR', 'SABVL', 1).
synapse('AVKL', 'ADER', 1).
synapse('AVKL', 'AQR', 2).
synapse('AVKL', 'AVBL', 1).
synapse('AVKL', 'AVEL', 2).
synapse('AVKL', 'AVER', 1).
synapse('AVKL', 'AVKR', 2).
synapse('AVKL', 'AVM', 1).
synapse('AVKL', 'DVA', 1).
synapse('AVKL', 'PDEL', 2).
synapse('AVKL', 'PDEL', 1).
synapse('AVKL', 'PDER', 1).
synapse('AVKL', 'PVM', 1).
synapse('AVKL', 'PVPL', 1).
synapse('AVKL', 'PVPR', 1).
synapse('AVKL', 'PVT', 2).
synapse('AVKL', 'RICL', 1).
synapse('AVKL', 'RICR', 1).
synapse('AVKL', 'RIGL', 1).
synapse('AVKL', 'RIML', 2).
synapse('AVKL', 'RIMR', 1).
synapse('AVKL', 'RMFR', 1).
synapse('AVKL', 'SAADR', 1).
synapse('AVKL', 'SIAVR', 1).
synapse('AVKL', 'SMBDL', 1).
synapse('AVKL', 'SMBDR', 1).
synapse('AVKL', 'SMBVR', 1).
synapse('AVKL', 'SMDDR', 1).
synapse('AVKL', 'VB1', 4).
synapse('AVKL', 'VB10', 1).
synapse('AVKR', 'ADEL', 1).
synapse('AVKR', 'AQR', 1).
synapse('AVKR', 'AVKL', 2).
synapse('AVKR', 'BDUL', 1).
synapse('AVKR', 'MUS', 1).
synapse('AVKR', 'MUS', 1).
synapse('AVKR', 'PVPL', 6).
synapse('AVKR', 'PVQL', 1).
synapse('AVKR', 'RICL', 1).
synapse('AVKR', 'RIGR', 1).
synapse('AVKR', 'RIML', 2).
synapse('AVKR', 'RIMR', 2).
synapse('AVKR', 'RMDR', 1).
synapse('AVKR', 'RMFL', 1).
synapse('AVKR', 'SAADL', 1).
synapse('AVKR', 'SMBDL', 1).
synapse('AVKR', 'SMBDL', 1).
synapse('AVKR', 'SMBDR', 2).
synapse('AVKR', 'SMBVR', 1).
synapse('AVKR', 'SMDDL', 1).
synapse('AVKR', 'SMDDR', 2).
synapse('AVL', 'AVEL', 1).
synapse('AVL', 'AVFR', 1).
synapse('AVL', 'DA2', 1).
synapse('AVL', 'DD1', 1).
synapse('AVL', 'DD6', 2).
synapse('AVL', 'DVB', 1).
synapse('AVL', 'DVC', 9).
synapse('AVL', 'HSNR', 1).
synapse('AVL', 'MUS', 10).
synapse('AVL', 'PVM', 1).
synapse('AVL', 'PVPR', 1).
synapse('AVL', 'PVWL', 1).
synapse('AVL', 'SABD', 1).
synapse('AVL', 'SABD', 4).
synapse('AVL', 'SABVL', 4).
synapse('AVL', 'SABVR', 3).
synapse('AVL', 'VD12', 4).
synapse('AVM', 'ADER', 1).
synapse('AVM', 'ADER', 1).
synapse('AVM', 'ALML', 1).
synapse('AVM', 'ALMR', 1).
synapse('AVM', 'AVBL', 6).
synapse('AVM', 'AVBR', 2).
synapse('AVM', 'AVBR', 4).
synapse('AVM', 'AVDL', 2).
synapse('AVM', 'AVJR', 1).
synapse('AVM', 'BDUL', 2).
synapse('AVM', 'BDUL', 1).
synapse('AVM', 'BDUR', 2).
synapse('AVM', 'BDUR', 2).
synapse('AVM', 'DA1', 1).
synapse('AVM', 'PVCL', 4).
synapse('AVM', 'PVCR', 1).
synapse('AVM', 'PVCR', 4).
synapse('AVM', 'PVNL', 1).
synapse('AVM', 'PVR', 3).
synapse('AVM', 'RID', 1).
synapse('AVM', 'SIBVL', 1).
synapse('AVM', 'VA1', 2).
synapse('AWAL', 'ADAL', 1).
synapse('AWAL', 'AFDL', 1).
synapse('AWAL', 'AFDL', 4).
synapse('AWAL', 'AIAL', 1).
synapse('AWAL', 'AIYL', 1).
synapse('AWAL', 'AIZL', 3).
synapse('AWAL', 'AIZL', 7).
synapse('AWAL', 'ASEL', 4).
synapse('AWAL', 'ASGL', 1).
synapse('AWAL', 'AWAR', 1).
synapse('AWAL', 'AWBL', 1).
synapse('AWAR', 'ADFR', 3).
synapse('AWAR', 'AFDR', 1).
synapse('AWAR', 'AFDR', 6).
synapse('AWAR', 'AIAR', 1).
synapse('AWAR', 'AIYR', 2).
synapse('AWAR', 'AIZR', 1).
synapse('AWAR', 'AIZR', 2).
synapse('AWAR', 'AIZR', 5).
synapse('AWAR', 'ASEL', 1).
synapse('AWAR', 'ASER', 2).
synapse('AWAR', 'AUAR', 1).
synapse('AWAR', 'AWAL', 1).
synapse('AWAR', 'AWBR', 1).
synapse('AWAR', 'RIFR', 2).
synapse('AWAR', 'RIGR', 1).
synapse('AWAR', 'RIR', 2).
synapse('AWBL', 'ADFL', 1).
synapse('AWBL', 'ADFL', 8).
synapse('AWBL', 'AIBR', 1).
synapse('AWBL', 'AIZL', 3).
synapse('AWBL', 'AIZL', 6).
synapse('AWBL', 'AUAL', 1).
synapse('AWBL', 'AVBL', 1).
synapse('AWBL', 'AWBR', 1).
synapse('AWBL', 'RIAL', 1).
synapse('AWBL', 'RIAL', 2).
synapse('AWBL', 'RMGL', 1).
synapse('AWBL', 'SMBDL', 1).
synapse('AWBR', 'ADFR', 1).
synapse('AWBR', 'ADFR', 3).
synapse('AWBR', 'AIZR', 1).
synapse('AWBR', 'AIZR', 3).
synapse('AWBR', 'ASGR', 1).
synapse('AWBR', 'ASHR', 2).
synapse('AWBR', 'AUAR', 1).
synapse('AWBR', 'AVBR', 2).
synapse('AWBR', 'AWBL', 1).
synapse('AWBR', 'RIAR', 1).
synapse('AWBR', 'RICL', 1).
synapse('AWBR', 'RIR', 2).
synapse('AWBR', 'RMGR', 1).
synapse('AWBR', 'SMBVR', 1).
synapse('AWCL', 'AIAL', 2).
synapse('AWCL', 'AIAR', 3).
synapse('AWCL', 'AIAR', 1).
synapse('AWCL', 'AIBL', 1).
synapse('AWCL', 'AIBL', 1).
synapse('AWCL', 'AIBR', 1).
synapse('AWCL', 'AIYL', 7).
synapse('AWCL', 'AIYL', 3).
synapse('AWCL', 'ASEL', 1).
synapse('AWCL', 'AVAL', 1).
synapse('AWCL', 'AWCR', 1).
synapse('AWCL', 'RIAL', 2).
synapse('AWCL', 'RIAL', 1).
synapse('AWCR', 'AIAR', 1).
synapse('AWCR', 'AIAR', 1).
synapse('AWCR', 'AIBR', 4).
synapse('AWCR', 'AIYL', 1).
synapse('AWCR', 'AIYL', 3).
synapse('AWCR', 'AIYR', 3).
synapse('AWCR', 'AIYR', 6).
synapse('AWCR', 'ASEL', 1).
synapse('AWCR', 'ASGR', 1).
synapse('AWCR', 'AWCL', 1).
synapse('AWCR', 'AWCL', 4).
synapse('BAGL', 'AIBL', 1).
synapse('BAGL', 'AVAR', 1).
synapse('BAGL', 'AVAR', 1).
synapse('BAGL', 'AVEL', 1).
synapse('BAGL', 'AVER', 1).
synapse('BAGL', 'AVER', 3).
synapse('BAGL', 'BAGR', 1).
synapse('BAGL', 'BAGR', 1).
synapse('BAGL', 'RIAR', 2).
synapse('BAGL', 'RIAR', 3).
synapse('BAGL', 'RIBL', 1).
synapse('BAGL', 'RIBR', 1).
synapse('BAGL', 'RIBR', 6).
synapse('BAGL', 'RIGL', 1).
synapse('BAGL', 'RIGR', 3).
synapse('BAGL', 'RIGR', 1).
synapse('BAGL', 'RIGR', 1).
synapse('BAGL', 'RIR', 1).
synapse('BAGR', 'AIYL', 1).
synapse('BAGR', 'AVAL', 1).
synapse('BAGR', 'AVAL', 1).
synapse('BAGR', 'AVEL', 2).
synapse('BAGR', 'AVEL', 2).
synapse('BAGR', 'BAGL', 1).
synapse('BAGR', 'RIAL', 2).
synapse('BAGR', 'RIAL', 3).
synapse('BAGR', 'RIBL', 1).
synapse('BAGR', 'RIBL', 3).
synapse('BAGR', 'RIGL', 2).
synapse('BAGR', 'RIGL', 3).
synapse('BAGR', 'RIGL', 1).
synapse('BAGR', 'RIR', 1).
synapse('BDUL', 'ADEL', 3).
synapse('BDUL', 'AVHL', 1).
synapse('BDUL', 'AVJR', 1).
synapse('BDUL', 'HSNL', 1).
synapse('BDUL', 'PVNL', 2).
synapse('BDUL', 'PVNR', 2).
synapse('BDUL', 'SAADL', 1).
synapse('BDUL', 'URADL', 1).
synapse('BDUR', 'ADER', 1).
synapse('BDUR', 'ALMR', 1).
synapse('BDUR', 'AVAL', 3).
synapse('BDUR', 'AVHL', 1).
synapse('BDUR', 'AVJL', 2).
synapse('BDUR', 'HSNR', 1).
synapse('BDUR', 'HSNR', 3).
synapse('BDUR', 'PVCL', 1).
synapse('BDUR', 'PVCL', 1).
synapse('BDUR', 'PVNL', 2).
synapse('BDUR', 'PVNL', 2).
synapse('BDUR', 'PVNR', 1).
synapse('BDUR', 'SDQL', 1).
synapse('BDUR', 'URADR', 1).
synapse('CEPDL', 'AVER', 1).
synapse('CEPDL', 'AVER', 4).
synapse('CEPDL', 'IL1DL', 4).
synapse('CEPDL', 'OLLL', 2).
synapse('CEPDL', 'OLQDL', 6).
synapse('CEPDL', 'OLQDL', 1).
synapse('CEPDL', 'RIBL', 2).
synapse('CEPDL', 'RICL', 1).
synapse('CEPDL', 'RICL', 1).
synapse('CEPDL', 'RICR', 2).
synapse('CEPDL', 'RICR', 2).
synapse('CEPDL', 'RIH', 1).
synapse('CEPDL', 'RIPL', 2).
synapse('CEPDL', 'RIS', 1).
synapse('CEPDL', 'RMDVL', 1).
synapse('CEPDL', 'RMDVL', 2).
synapse('CEPDL', 'RMGL', 1).
synapse('CEPDL', 'RMGL', 3).
synapse('CEPDL', 'RMHR', 1).
synapse('CEPDL', 'RMHR', 3).
synapse('CEPDL', 'SIADR', 1).
synapse('CEPDL', 'SIADR', 1).
synapse('CEPDL', 'SMBDR', 1).
synapse('CEPDL', 'URADL', 2).
synapse('CEPDL', 'URBL', 4).
synapse('CEPDL', 'URYDL', 2).
synapse('CEPDR', 'AVEL', 6).
synapse('CEPDR', 'BDUR', 1).
synapse('CEPDR', 'IL1DR', 5).
synapse('CEPDR', 'IL1R', 1).
synapse('CEPDR', 'OLLR', 1).
synapse('CEPDR', 'OLLR', 7).
synapse('CEPDR', 'OLQDR', 5).
synapse('CEPDR', 'OLQDR', 2).
synapse('CEPDR', 'RIBR', 1).
synapse('CEPDR', 'RICL', 4).
synapse('CEPDR', 'RICR', 3).
synapse('CEPDR', 'RIH', 1).
synapse('CEPDR', 'RIS', 1).
synapse('CEPDR', 'RMDDL', 1).
synapse('CEPDR', 'RMDVR', 2).
synapse('CEPDR', 'RMGR', 1).
synapse('CEPDR', 'RMHL', 4).
synapse('CEPDR', 'RMHR', 1).
synapse('CEPDR', 'SIADL', 1).
synapse('CEPDR', 'SMBDR', 1).
synapse('CEPDR', 'URADR', 1).
synapse('CEPDR', 'URBR', 2).
synapse('CEPDR', 'URYDR', 1).
synapse('CEPVL', 'ADLL', 1).
synapse('CEPVL', 'AVER', 1).
synapse('CEPVL', 'AVER', 2).
synapse('CEPVL', 'IL1VL', 2).
synapse('CEPVL', 'OLLL', 4).
synapse('CEPVL', 'OLQVL', 6).
synapse('CEPVL', 'OLQVL', 1).
synapse('CEPVL', 'RICL', 1).
synapse('CEPVL', 'RICL', 6).
synapse('CEPVL', 'RICR', 4).
synapse('CEPVL', 'RIH', 1).
synapse('CEPVL', 'RIPL', 1).
synapse('CEPVL', 'RMDDL', 4).
synapse('CEPVL', 'RMHL', 1).
synapse('CEPVL', 'SIAVL', 1).
synapse('CEPVL', 'SIAVL', 1).
synapse('CEPVL', 'URAVL', 2).
synapse('CEPVR', 'ASGR', 1).
synapse('CEPVR', 'AVEL', 1).
synapse('CEPVR', 'AVEL', 4).
synapse('CEPVR', 'IL1VR', 1).
synapse('CEPVR', 'IL1VR', 1).
synapse('CEPVR', 'IL2VR', 2).
synapse('CEPVR', 'OLLR', 1).
synapse('CEPVR', 'OLLR', 6).
synapse('CEPVR', 'OLQVR', 3).
synapse('CEPVR', 'OLQVR', 1).
synapse('CEPVR', 'RICL', 2).
synapse('CEPVR', 'RICR', 2).
synapse('CEPVR', 'RICR', 2).
synapse('CEPVR', 'RIH', 1).
synapse('CEPVR', 'RIPR', 1).
synapse('CEPVR', 'RIVL', 1).
synapse('CEPVR', 'RMDDR', 2).
synapse('CEPVR', 'RMHR', 2).
synapse('CEPVR', 'SIAVR', 2).
synapse('CEPVR', 'URAVR', 1).
synapse('DA1', 'AVAL', 2).
synapse('DA1', 'AVAR', 6).
synapse('DA1', 'DA4', 1).
synapse('DA1', 'DD1', 4).
synapse('DA1', 'MUS', 16).
synapse('DA1', 'SABVL', 2).
synapse('DA1', 'SABVR', 3).
synapse('DA1', 'VD1', 17).
synapse('DA1', 'VD2', 1).
synapse('DA2', 'AS2', 1).
synapse('DA2', 'AS3', 1).
synapse('DA2', 'AVAL', 2).
synapse('DA2', 'AVAR', 2).
synapse('DA2', 'DD1', 1).
synapse('DA2', 'MUS', 15).
synapse('DA2', 'SABVL', 1).
synapse('DA2', 'VA1', 2).
synapse('DA2', 'VD1', 2).
synapse('DA2', 'VD2', 11).
synapse('DA2', 'VD3', 5).
synapse('DA3', 'AS4', 1).
synapse('DA3', 'AS4', 1).
synapse('DA3', 'AVAR', 2).
synapse('DA3', 'DA4', 2).
synapse('DA3', 'DB3', 1).
synapse('DA3', 'DD2', 1).
synapse('DA3', 'MUS', 30).
synapse('DA3', 'VD3', 25).
synapse('DA3', 'VD4', 6).
synapse('DA4', 'AVAL', 3).
synapse('DA4', 'AVAR', 2).
synapse('DA4', 'DA1', 1).
synapse('DA4', 'DA3', 1).
synapse('DA4', 'DB3', 1).
synapse('DA4', 'DB3', 1).
synapse('DA4', 'DD2', 1).
synapse('DA4', 'MUS', 26).
synapse('DA4', 'VB6', 1).
synapse('DA4', 'VD4', 12).
synapse('DA4', 'VD5', 15).
synapse('DA5', 'AS6', 2).
synapse('DA5', 'AVAL', 1).
synapse('DA5', 'AVAR', 5).
synapse('DA5', 'DB4', 1).
synapse('DA5', 'MUS', 17).
synapse('DA5', 'VA4', 1).
synapse('DA5', 'VA5', 2).
synapse('DA5', 'VD5', 1).
synapse('DA5', 'VD6', 16).
synapse('DA6', 'AVAL', 10).
synapse('DA6', 'AVAR', 2).
synapse('DA6', 'MUS', 6).
synapse('DA6', 'VD4', 4).
synapse('DA6', 'VD5', 3).
synapse('DA6', 'VD6', 3).
synapse('DA7', 'AVAL', 2).
synapse('DA8', 'AVAR', 1).
synapse('DA8', 'DA9', 1).
synapse('DA9', 'DA8', 1).
synapse('DA9', 'DD6', 1).
synapse('DA9', 'MUS', 1).
synapse('DA9', 'PDA', 1).
synapse('DA9', 'PHCL', 1).
synapse('DA9', 'RID', 1).
synapse('DA9', 'VD13', 1).
synapse('DB1', 'AIBR', 1).
synapse('DB1', 'AS1', 1).
synapse('DB1', 'AS2', 1).
synapse('DB1', 'AS3', 1).
synapse('DB1', 'AVBR', 3).
synapse('DB1', 'DB2', 1).
synapse('DB1', 'DB4', 1).
synapse('DB1', 'DD1', 10).
synapse('DB1', 'DVA', 1).
synapse('DB1', 'MUS', 3).
synapse('DB1', 'RID', 1).
synapse('DB1', 'RIS', 1).
synapse('DB1', 'VB3', 1).
synapse('DB1', 'VB4', 1).
synapse('DB1', 'VD1', 21).
synapse('DB1', 'VD2', 15).
synapse('DB1', 'VD3', 1).
synapse('DB2', 'AVBR', 1).
synapse('DB2', 'DA3', 5).
synapse('DB2', 'DB1', 1).
synapse('DB2', 'DB3', 6).
synapse('DB2', 'DD2', 2).
synapse('DB2', 'MUS', 24).
synapse('DB2', 'VB1', 2).
synapse('DB2', 'VD3', 23).
synapse('DB2', 'VD4', 14).
synapse('DB2', 'VD5', 1).
synapse('DB3', 'AS4', 1).
synapse('DB3', 'AS5', 1).
synapse('DB3', 'AVBL', 1).
synapse('DB3', 'AVBR', 1).
synapse('DB3', 'DA4', 1).
synapse('DB3', 'DB2', 6).
synapse('DB3', 'DB4', 1).
synapse('DB3', 'DD2', 4).
synapse('DB3', 'DD3', 10).
synapse('DB3', 'MUS', 25).
synapse('DB3', 'VD4', 9).
synapse('DB3', 'VD5', 26).
synapse('DB3', 'VD6', 7).
synapse('DB4', 'AVBL', 1).
synapse('DB4', 'AVBR', 1).
synapse('DB4', 'DB1', 1).
synapse('DB4', 'DB3', 1).
synapse('DB4', 'DD3', 3).
synapse('DB4', 'MUS', 6).
synapse('DB4', 'VB2', 1).
synapse('DB4', 'VB4', 1).
synapse('DB4', 'VD6', 13).
synapse('DB5', 'AVAR', 2).
synapse('DB5', 'AVBL', 1).
synapse('DB5', 'AVBR', 1).
synapse('DB6', 'AVAL', 3).
synapse('DB6', 'AVBL', 2).
synapse('DB6', 'AVBR', 1).
synapse('DB7', 'AVBL', 2).
synapse('DB7', 'AVBR', 1).
synapse('DB7', 'VD13', 2).
synapse('DD1', 'AVBR', 1).
synapse('DD1', 'DA2', 2).
synapse('DD1', 'DD2', 1).
synapse('DD1', 'MUS', 34).
synapse('DD1', 'VD1', 4).
synapse('DD1', 'VD2', 1).
synapse('DD1', 'VD2', 2).
synapse('DD2', 'DA3', 1).
synapse('DD2', 'DD1', 1).
synapse('DD2', 'DD3', 2).
synapse('DD2', 'MUS', 28).
synapse('DD2', 'VD3', 1).
synapse('DD2', 'VD4', 1).
synapse('DD2', 'VD4', 2).
synapse('DD3', 'DD2', 2).
synapse('DD3', 'DD4', 1).
synapse('DD3', 'MUS', 32).
synapse('DD4', 'DD3', 1).
synapse('DD4', 'VC3', 1).
synapse('DD4', 'VD8', 1).
synapse('DD5', 'MUS', 1).
synapse('DD5', 'VB8', 1).
synapse('DD5', 'VD9', 1).
synapse('DD5', 'VD10', 1).
synapse('DD6', 'MUS', 1).
synapse('DVA', 'AIZL', 3).
synapse('DVA', 'AQR', 1).
synapse('DVA', 'AQR', 3).
synapse('DVA', 'AUAL', 1).
synapse('DVA', 'AUAR', 1).
synapse('DVA', 'AVAL', 3).
synapse('DVA', 'AVAR', 1).
synapse('DVA', 'AVBL', 1).
synapse('DVA', 'AVBL', 1).
synapse('DVA', 'AVBR', 1).
synapse('DVA', 'AVEL', 3).
synapse('DVA', 'AVEL', 6).
synapse('DVA', 'AVER', 2).
synapse('DVA', 'AVER', 3).
synapse('DVA', 'DB1', 1).
synapse('DVA', 'DB2', 1).
synapse('DVA', 'DB3', 2).
synapse('DVA', 'DB4', 1).
synapse('DVA', 'DB5', 1).
synapse('DVA', 'DB6', 2).
synapse('DVA', 'DB7', 1).
synapse('DVA', 'DB7', 1).
synapse('DVA', 'PDEL', 1).
synapse('DVA', 'PDEL', 2).
synapse('DVA', 'PVCL', 3).
synapse('DVA', 'PVCL', 1).
synapse('DVA', 'PVCR', 1).
synapse('DVA', 'PVR', 1).
synapse('DVA', 'PVR', 2).
synapse('DVA', 'PVR', 2).
synapse('DVA', 'RIAL', 1).
synapse('DVA', 'RIAR', 1).
synapse('DVA', 'RIAR', 1).
synapse('DVA', 'RIMR', 1).
synapse('DVA', 'RIR', 3).
synapse('DVA', 'SAADR', 1).
synapse('DVA', 'SAAVL', 1).
synapse('DVA', 'SAAVR', 1).
synapse('DVA', 'SABD', 1).
synapse('DVA', 'SMBDL', 3).
synapse('DVA', 'SMBDR', 2).
synapse('DVA', 'SMBVL', 3).
synapse('DVA', 'SMBVR', 2).
synapse('DVA', 'VA2', 1).
synapse('DVA', 'VA12', 1).
synapse('DVA', 'VB1', 1).
synapse('DVA', 'VB11', 2).
synapse('DVB', 'AS9', 7).
synapse('DVB', 'AVL', 1).
synapse('DVB', 'AVL', 2).
synapse('DVB', 'AVL', 3).
synapse('DVB', 'DA8', 2).
synapse('DVB', 'DA8', 2).
synapse('DVB', 'DD6', 3).
synapse('DVB', 'DVC', 3).
synapse('DVB', 'MUS', 1).
synapse('DVB', 'MUS', 4).
synapse('DVB', 'PDA', 1).
synapse('DVB', 'PHCL', 1).
synapse('DVB', 'PVPL', 1).
synapse('DVB', 'PVPL', 1).
synapse('DVB', 'VA9', 1).
synapse('DVB', 'VB9', 1).
synapse('DVC', 'AIBL', 1).
synapse('DVC', 'AIBL', 1).
synapse('DVC', 'AIBR', 2).
synapse('DVC', 'AIBR', 3).
synapse('DVC', 'AVAL', 5).
synapse('DVC', 'AVAR', 7).
synapse('DVC', 'AVBL', 1).
synapse('DVC', 'AVKL', 2).
synapse('DVC', 'AVKR', 1).
synapse('DVC', 'AVL', 9).
synapse('DVC', 'PVPL', 2).
synapse('DVC', 'PVPR', 13).
synapse('DVC', 'PVT', 1).
synapse('DVC', 'RIBL', 1).
synapse('DVC', 'RIBR', 1).
synapse('DVC', 'RIGL', 1).
synapse('DVC', 'RIGL', 4).
synapse('DVC', 'RIGR', 5).
synapse('DVC', 'RMFL', 2).
synapse('DVC', 'RMFR', 4).
synapse('DVC', 'VA9', 1).
synapse('DVC', 'VD1', 5).
synapse('DVC', 'VD10', 4).
synapse('FLPL', 'ADEL', 2).
synapse('FLPL', 'ADER', 2).
synapse('FLPL', 'AIBL', 1).
synapse('FLPL', 'AIBL', 1).
synapse('FLPL', 'AIBR', 2).
synapse('FLPL', 'AVAL', 1).
synapse('FLPL', 'AVAL', 4).
synapse('FLPL', 'AVAL', 10).
synapse('FLPL', 'AVAR', 17).
synapse('FLPL', 'AVBL', 1).
synapse('FLPL', 'AVBL', 3).
synapse('FLPL', 'AVBR', 1).
synapse('FLPL', 'AVBR', 4).
synapse('FLPL', 'AVDL', 1).
synapse('FLPL', 'AVDL', 6).
synapse('FLPL', 'AVDR', 13).
synapse('FLPL', 'DVA', 1).
synapse('FLPL', 'FLPR', 1).
synapse('FLPL', 'FLPR', 2).
synapse('FLPL', 'RIH', 1).
synapse('FLPR', 'ADER', 1).
synapse('FLPR', 'ADER', 1).
synapse('FLPR', 'AIBR', 1).
synapse('FLPR', 'AVAL', 2).
synapse('FLPR', 'AVAL', 10).
synapse('FLPR', 'AVAR', 5).
synapse('FLPR', 'AVBL', 5).
synapse('FLPR', 'AVBR', 1).
synapse('FLPR', 'AVDL', 1).
synapse('FLPR', 'AVDL', 2).
synapse('FLPR', 'AVDL', 8).
synapse('FLPR', 'AVDR', 1).
synapse('FLPR', 'AVDR', 1).
synapse('FLPR', 'AVEL', 4).
synapse('FLPR', 'AVER', 2).
synapse('FLPR', 'AVJR', 1).
synapse('FLPR', 'DVA', 1).
synapse('FLPR', 'FLPL', 2).
synapse('FLPR', 'FLPL', 2).
synapse('FLPR', 'PVCL', 2).
synapse('FLPR', 'VB1', 1).
synapse('FLPR', 'VB1', 0).
synapse('HSNL', 'AIAL', 1).
synapse('HSNL', 'AIZL', 2).
synapse('HSNL', 'AIZR', 1).
synapse('HSNL', 'ASHL', 1).
synapse('HSNL', 'ASHR', 2).
synapse('HSNL', 'ASJR', 1).
synapse('HSNL', 'ASKL', 1).
synapse('HSNL', 'AVDR', 2).
synapse('HSNL', 'AVFL', 1).
synapse('HSNL', 'AVFL', 5).
synapse('HSNL', 'AVJL', 1).
synapse('HSNL', 'AVJL', 1).
synapse('HSNL', 'AWBL', 1).
synapse('HSNL', 'AWBL', 1).
synapse('HSNL', 'AWBR', 2).
synapse('HSNL', 'HSNR', 1).
synapse('HSNL', 'HSNR', 3).
synapse('HSNL', 'MUS', 7).
synapse('HSNL', 'RIFL', 3).
synapse('HSNL', 'RIML', 2).
synapse('HSNL', 'SABVL', 2).
synapse('HSNL', 'VC5', 3).
synapse('HSNR', 'AIBL', 1).
synapse('HSNR', 'AIBR', 1).
synapse('HSNR', 'AIZL', 1).
synapse('HSNR', 'AIZR', 1).
synapse('HSNR', 'AS5', 1).
synapse('HSNR', 'ASHL', 2).
synapse('HSNR', 'AVDR', 1).
synapse('HSNR', 'AVFL', 1).
synapse('HSNR', 'AVFL', 1).
synapse('HSNR', 'AVJL', 1).
synapse('HSNR', 'AVL', 1).
synapse('HSNR', 'AWBL', 1).
synapse('HSNR', 'BDUR', 1).
synapse('HSNR', 'DA5', 1).
synapse('HSNR', 'DA6', 1).
synapse('HSNR', 'HSNL', 1).
synapse('HSNR', 'HSNL', 1).
synapse('HSNR', 'MUS', 5).
synapse('HSNR', 'MUS', 1).
synapse('HSNR', 'PVNR', 1).
synapse('HSNR', 'PVNR', 1).
synapse('HSNR', 'PVNR', 1).
synapse('HSNR', 'PVQR', 1).
synapse('HSNR', 'RIFR', 1).
synapse('HSNR', 'RIFR', 3).
synapse('HSNR', 'RMGR', 1).
synapse('HSNR', 'SABD', 1).
synapse('HSNR', 'SABVR', 1).
synapse('HSNR', 'VA6', 1).
synapse('HSNR', 'VC2', 1).
synapse('HSNR', 'VC2', 2).
synapse('HSNR', 'VC3', 1).
synapse('HSNR', 'VD4', 2).
synapse('IL1DL', 'IL1DR', 1).
synapse('IL1DL', 'IL1L', 1).
synapse('IL1DL', 'MUS', 1).
synapse('IL1DL', 'MUS', 4).
synapse('IL1DL', 'OLLL', 1).
synapse('IL1DL', 'PVR', 1).
synapse('IL1DL', 'RIH', 1).
synapse('IL1DL', 'RIPL', 2).
synapse('IL1DL', 'RMDDR', 1).
synapse('IL1DL', 'RMDVL', 4).
synapse('IL1DL', 'RMEV', 1).
synapse('IL1DL', 'URYDL', 1).
synapse('IL1DR', 'IL1DL', 1).
synapse('IL1DR', 'IL1R', 1).
synapse('IL1DR', 'MUS', 1).
synapse('IL1DR', 'MUS', 6).
synapse('IL1DR', 'OLLR', 1).
synapse('IL1DR', 'RIPR', 5).
synapse('IL1DR', 'RMDVR', 5).
synapse('IL1DR', 'RMEV', 1).
synapse('IL1L', 'AVER', 2).
synapse('IL1L', 'IL1DL', 1).
synapse('IL1L', 'IL1DL', 1).
synapse('IL1L', 'IL1VL', 1).
synapse('IL1L', 'MUS', 1).
synapse('IL1L', 'MUS', 12).
synapse('IL1L', 'RMDDL', 5).
synapse('IL1L', 'RMDL', 1).
synapse('IL1L', 'RMDR', 3).
synapse('IL1L', 'RMDVL', 4).
synapse('IL1L', 'RMDVR', 2).
synapse('IL1L', 'RMER', 1).
synapse('IL1R', 'AVEL', 1).
synapse('IL1R', 'AVER', 1).
synapse('IL1R', 'IL1DR', 1).
synapse('IL1R', 'IL1DR', 1).
synapse('IL1R', 'IL1VR', 1).
synapse('IL1R', 'MUS', 1).
synapse('IL1R', 'MUS', 12).
synapse('IL1R', 'RMDDL', 3).
synapse('IL1R', 'RMDDR', 2).
synapse('IL1R', 'RMDL', 1).
synapse('IL1R', 'RMDL', 3).
synapse('IL1R', 'RMDR', 2).
synapse('IL1R', 'RMDVL', 1).
synapse('IL1R', 'RMDVR', 4).
synapse('IL1R', 'RMEL', 2).
synapse('IL1R', 'RMHL', 1).
synapse('IL1R', 'URXR', 2).
synapse('IL1VL', 'IL1L', 1).
synapse('IL1VL', 'IL1L', 1).
synapse('IL1VL', 'IL1VR', 1).
synapse('IL1VL', 'MUS', 3).
synapse('IL1VL', 'MUS', 6).
synapse('IL1VL', 'RIPL', 4).
synapse('IL1VL', 'RMDDL', 5).
synapse('IL1VL', 'RMED', 1).
synapse('IL1VL', 'URYVL', 1).
synapse('IL1VR', 'IL1R', 1).
synapse('IL1VR', 'IL1R', 1).
synapse('IL1VR', 'IL1VL', 1).
synapse('IL1VR', 'IL2R', 1).
synapse('IL1VR', 'IL2VR', 1).
synapse('IL1VR', 'MUS', 1).
synapse('IL1VR', 'MUS', 9).
synapse('IL1VR', 'RIPR', 1).
synapse('IL1VR', 'RIPR', 5).
synapse('IL1VR', 'RMDDR', 10).
synapse('IL1VR', 'RMER', 1).
synapse('IL2DL', 'AUAL', 1).
synapse('IL2DL', 'IL1DL', 7).
synapse('IL2DL', 'OLQDL', 2).
synapse('IL2DL', 'RIBL', 1).
synapse('IL2DL', 'RIPL', 10).
synapse('IL2DL', 'RMEL', 4).
synapse('IL2DL', 'RMER', 3).
synapse('IL2DL', 'URADL', 1).
synapse('IL2DL', 'URADL', 2).
synapse('IL2DR', 'CEPDR', 1).
synapse('IL2DR', 'IL1DR', 7).
synapse('IL2DR', 'RICR', 1).
synapse('IL2DR', 'RIPR', 11).
synapse('IL2DR', 'RMED', 1).
synapse('IL2DR', 'RMEL', 2).
synapse('IL2DR', 'RMER', 2).
synapse('IL2DR', 'RMEV', 1).
synapse('IL2DR', 'URADR', 3).
synapse('IL2L', 'ADEL', 2).
synapse('IL2L', 'AVEL', 1).
synapse('IL2L', 'IL1L', 1).
synapse('IL2L', 'OLQDL', 2).
synapse('IL2L', 'OLQDL', 3).
synapse('IL2L', 'OLQVL', 2).
synapse('IL2L', 'OLQVL', 6).
synapse('IL2L', 'RICL', 1).
synapse('IL2L', 'RIH', 7).
synapse('IL2L', 'RMDL', 1).
synapse('IL2L', 'RMDL', 2).
synapse('IL2L', 'RMDR', 1).
synapse('IL2L', 'RMER', 2).
synapse('IL2L', 'RMEV', 2).
synapse('IL2L', 'RMGL', 1).
synapse('IL2L', 'URXL', 2).
synapse('IL2R', 'ADER', 1).
synapse('IL2R', 'ADER', 1).
synapse('IL2R', 'IL1R', 1).
synapse('IL2R', 'IL1VR', 1).
synapse('IL2R', 'OLLR', 1).
synapse('IL2R', 'OLLR', 1).
synapse('IL2R', 'OLQDR', 2).
synapse('IL2R', 'OLQVR', 2).
synapse('IL2R', 'OLQVR', 5).
synapse('IL2R', 'RIH', 6).
synapse('IL2R', 'RMDL', 1).
synapse('IL2R', 'RMDL', 1).
synapse('IL2R', 'RMEL', 2).
synapse('IL2R', 'RMEV', 1).
synapse('IL2R', 'RMGR', 1).
synapse('IL2R', 'URBR', 1).
synapse('IL2R', 'URXR', 1).
synapse('IL2VL', 'BAGR', 1).
synapse('IL2VL', 'IL1VL', 7).
synapse('IL2VL', 'IL2L', 1).
synapse('IL2VL', 'OLQVL', 1).
synapse('IL2VL', 'RIAL', 1).
synapse('IL2VL', 'RIH', 2).
synapse('IL2VL', 'RIPL', 11).
synapse('IL2VL', 'RMEL', 1).
synapse('IL2VL', 'RMEL', 1).
synapse('IL2VL', 'RMER', 4).
synapse('IL2VL', 'RMEV', 1).
synapse('IL2VL', 'URAVL', 3).
synapse('IL2VR', 'IL1VR', 6).
synapse('IL2VR', 'OLQVR', 1).
synapse('IL2VR', 'OLQVR', 1).
synapse('IL2VR', 'RIAR', 2).
synapse('IL2VR', 'RIH', 1).
synapse('IL2VR', 'RIH', 2).
synapse('IL2VR', 'RIPR', 1).
synapse('IL2VR', 'RIPR', 14).
synapse('IL2VR', 'RMEL', 3).
synapse('IL2VR', 'RMER', 2).
synapse('IL2VR', 'RMEV', 3).
synapse('IL2VR', 'URAVR', 4).
synapse('IL2VR', 'URXR', 1).
synapse('LUAL', 'AVAL', 1).
synapse('LUAL', 'AVAL', 5).
synapse('LUAL', 'AVAR', 1).
synapse('LUAL', 'AVAR', 5).
synapse('LUAL', 'AVDL', 4).
synapse('LUAL', 'AVDR', 2).
synapse('LUAL', 'AVJL', 1).
synapse('LUAL', 'PHBL', 1).
synapse('LUAL', 'PLML', 1).
synapse('LUAL', 'PVNL', 1).
synapse('LUAL', 'PVR', 1).
synapse('LUAL', 'PVWL', 1).
synapse('LUAR', 'AVAL', 3).
synapse('LUAR', 'AVAR', 7).
synapse('LUAR', 'AVDL', 1).
synapse('LUAR', 'AVDR', 3).
synapse('LUAR', 'AVJR', 1).
synapse('LUAR', 'PLMR', 1).
synapse('LUAR', 'PQR', 1).
synapse('LUAR', 'PVCR', 3).
synapse('LUAR', 'PVR', 1).
synapse('LUAR', 'PVR', 1).
synapse('LUAR', 'PVWL', 1).
synapse('OLLL', 'AVER', 3).
synapse('OLLL', 'AVER', 18).
synapse('OLLL', 'CEPDL', 3).
synapse('OLLL', 'CEPVL', 4).
synapse('OLLL', 'IL1DL', 1).
synapse('OLLL', 'IL1VL', 2).
synapse('OLLL', 'OLLR', 2).
synapse('OLLL', 'RIBL', 8).
synapse('OLLL', 'RIGL', 1).
synapse('OLLL', 'RMDDL', 7).
synapse('OLLL', 'RMDL', 2).
synapse('OLLL', 'RMDVL', 1).
synapse('OLLL', 'RMEL', 2).
synapse('OLLL', 'SMDDL', 2).
synapse('OLLL', 'SMDDL', 1).
synapse('OLLL', 'SMDDR', 3).
synapse('OLLL', 'SMDDR', 1).
synapse('OLLL', 'SMDVR', 4).
synapse('OLLL', 'URYDL', 1).
synapse('OLLR', 'AVEL', 1).
synapse('OLLR', 'AVEL', 15).
synapse('OLLR', 'CEPDR', 1).
synapse('OLLR', 'CEPDR', 1).
synapse('OLLR', 'CEPVR', 6).
synapse('OLLR', 'IL1DR', 1).
synapse('OLLR', 'IL1DR', 2).
synapse('OLLR', 'IL1VR', 1).
synapse('OLLR', 'IL2R', 1).
synapse('OLLR', 'OLLL', 2).
synapse('OLLR', 'RIBR', 2).
synapse('OLLR', 'RIBR', 8).
synapse('OLLR', 'RIGR', 1).
synapse('OLLR', 'RMDDR', 10).
synapse('OLLR', 'RMDL', 3).
synapse('OLLR', 'RMDVR', 3).
synapse('OLLR', 'RMER', 2).
synapse('OLLR', 'SMDDR', 1).
synapse('OLLR', 'SMDVL', 4).
synapse('OLLR', 'SMDVR', 3).
synapse('OLQDL', 'CEPDL', 1).
synapse('OLQDL', 'RIBL', 2).
synapse('OLQDL', 'RICR', 1).
synapse('OLQDL', 'RIGL', 1).
synapse('OLQDL', 'RMDDR', 1).
synapse('OLQDL', 'RMDDR', 3).
synapse('OLQDL', 'RMDVL', 1).
synapse('OLQDL', 'SIBVL', 3).
synapse('OLQDL', 'URBL', 1).
synapse('OLQDR', 'CEPDR', 2).
synapse('OLQDR', 'RIBR', 2).
synapse('OLQDR', 'RICL', 1).
synapse('OLQDR', 'RICR', 1).
synapse('OLQDR', 'RIGR', 1).
synapse('OLQDR', 'RIH', 1).
synapse('OLQDR', 'RMDDL', 1).
synapse('OLQDR', 'RMDDL', 2).
synapse('OLQDR', 'RMDVR', 1).
synapse('OLQDR', 'RMHR', 1).
synapse('OLQDR', 'SIBVR', 2).
synapse('OLQDR', 'URBR', 1).
synapse('OLQVL', 'ADLL', 1).
synapse('OLQVL', 'CEPVL', 1).
synapse('OLQVL', 'IL1VL', 1).
synapse('OLQVL', 'IL1VL', 1).
synapse('OLQVL', 'IL2VL', 1).
synapse('OLQVL', 'RIBL', 1).
synapse('OLQVL', 'RICL', 1).
synapse('OLQVL', 'RIGL', 1).
synapse('OLQVL', 'RIH', 1).
synapse('OLQVL', 'RIPL', 1).
synapse('OLQVL', 'RMDDL', 1).
synapse('OLQVL', 'RMDVR', 1).
synapse('OLQVL', 'RMDVR', 3).
synapse('OLQVL', 'SIBDL', 3).
synapse('OLQVL', 'URBL', 1).
synapse('OLQVR', 'CEPVR', 1).
synapse('OLQVR', 'IL1VR', 1).
synapse('OLQVR', 'RIBR', 1).
synapse('OLQVR', 'RICR', 1).
synapse('OLQVR', 'RIGR', 1).
synapse('OLQVR', 'RIH', 2).
synapse('OLQVR', 'RIPR', 2).
synapse('OLQVR', 'RMDDR', 1).
synapse('OLQVR', 'RMDVL', 4).
synapse('OLQVR', 'RMER', 1).
synapse('OLQVR', 'SIBDR', 4).
synapse('OLQVR', 'URBR', 1).
synapse('PDA', 'AS11', 1).
synapse('PDA', 'DA9', 1).
synapse('PDA', 'DA9', 1).
synapse('PDA', 'DD6', 1).
synapse('PDA', 'MUS', 2).
synapse('PDA', 'PVNR', 1).
synapse('PDA', 'VD13', 3).
synapse('PDB', 'AS11', 2).
synapse('PDB', 'MUS', 2).
synapse('PDB', 'RID', 2).
synapse('PDB', 'VD13', 2).
synapse('PDB', 'VD13', 2).
synapse('PDEL', 'AVKL', 1).
synapse('PDEL', 'AVKL', 5).
synapse('PDEL', 'DVA', 16).
synapse('PDEL', 'DVA', 8).
synapse('PDEL', 'PDER', 1).
synapse('PDEL', 'PDER', 3).
synapse('PDEL', 'PVCR', 1).
synapse('PDEL', 'PVM', 2).
synapse('PDEL', 'PVM', 1).
synapse('PDEL', 'PVR', 2).
synapse('PDEL', 'VA9', 1).
synapse('PDEL', 'VD11', 1).
synapse('PDER', 'AVKL', 16).
synapse('PDER', 'DVA', 19).
synapse('PDER', 'DVA', 16).
synapse('PDER', 'PDEL', 3).
synapse('PDER', 'PVCL', 1).
synapse('PDER', 'PVCR', 1).
synapse('PDER', 'PVM', 1).
synapse('PDER', 'VA8', 1).
synapse('PDER', 'VD9', 1).
synapse('PHAL', 'AVDR', 1).
synapse('PHAL', 'AVFL', 3).
synapse('PHAL', 'AVG', 1).
synapse('PHAL', 'AVG', 4).
synapse('PHAL', 'AVHL', 1).
synapse('PHAL', 'AVHR', 1).
synapse('PHAL', 'DVA', 2).
synapse('PHAL', 'PHAR', 5).
synapse('PHAL', 'PHAR', 2).
synapse('PHAL', 'PHBL', 5).
synapse('PHAL', 'PHBR', 5).
synapse('PHAL', 'PVQL', 2).
synapse('PHAR', 'AVG', 1).
synapse('PHAR', 'AVG', 2).
synapse('PHAR', 'AVHR', 1).
synapse('PHAR', 'DA8', 1).
synapse('PHAR', 'DVA', 1).
synapse('PHAR', 'DVA', 1).
synapse('PHAR', 'PHAL', 2).
synapse('PHAR', 'PHAL', 1).
synapse('PHAR', 'PHAL', 5).
synapse('PHAR', 'PHBL', 1).
synapse('PHAR', 'PHBR', 5).
synapse('PHAR', 'PVPL', 3).
synapse('PHAR', 'PVQL', 2).
synapse('PHBL', 'AVAL', 9).
synapse('PHBL', 'AVAR', 6).
synapse('PHBL', 'AVDL', 1).
synapse('PHBL', 'PHBR', 1).
synapse('PHBL', 'PHBR', 3).
synapse('PHBL', 'PVCL', 13).
synapse('PHBL', 'VA12', 1).
synapse('PHBR', 'AVAL', 7).
synapse('PHBR', 'AVAR', 7).
synapse('PHBR', 'AVDL', 1).
synapse('PHBR', 'AVDR', 1).
synapse('PHBR', 'AVFL', 1).
synapse('PHBR', 'AVHL', 1).
synapse('PHBR', 'DA8', 1).
synapse('PHBR', 'PHBL', 3).
synapse('PHBR', 'PHBL', 1).
synapse('PHBR', 'PVCL', 6).
synapse('PHBR', 'PVCR', 3).
synapse('PHBR', 'VA12', 2).
synapse('PHCL', 'AVAL', 1).
synapse('PHCL', 'DA9', 1).
synapse('PHCL', 'DA9', 7).
synapse('PHCL', 'DVA', 4).
synapse('PHCL', 'DVA', 2).
synapse('PHCL', 'LUAL', 1).
synapse('PHCL', 'PHCR', 1).
synapse('PHCL', 'PLML', 1).
synapse('PHCL', 'PVCL', 2).
synapse('PHCL', 'VA12', 2).
synapse('PHCL', 'VA12', 1).
synapse('PHCR', 'AVHR', 1).
synapse('PHCR', 'DA9', 2).
synapse('PHCR', 'DVA', 3).
synapse('PHCR', 'DVA', 5).
synapse('PHCR', 'LUAR', 1).
synapse('PHCR', 'PHCL', 1).
synapse('PHCR', 'PHCL', 1).
synapse('PHCR', 'PVCR', 8).
synapse('PHCR', 'PVCR', 1).
synapse('PHCR', 'VA12', 1).
synapse('PHCR', 'VA12', 1).
synapse('PLML', 'HSNL', 1).
synapse('PLML', 'LUAL', 1).
synapse('PLML', 'PHCL', 1).
synapse('PLML', 'PVCL', 1).
synapse('PLMR', 'AS6', 1).
synapse('PLMR', 'AVAL', 1).
synapse('PLMR', 'AVAL', 3).
synapse('PLMR', 'AVAR', 1).
synapse('PLMR', 'AVDL', 1).
synapse('PLMR', 'AVDR', 4).
synapse('PLMR', 'DVA', 5).
synapse('PLMR', 'HSNR', 1).
synapse('PLMR', 'LUAR', 1).
synapse('PLMR', 'PDEL', 2).
synapse('PLMR', 'PDER', 3).
synapse('PLMR', 'PVCL', 2).
synapse('PLMR', 'PVCR', 1).
synapse('PLMR', 'PVR', 2).
synapse('PLNL', 'MUS', 1).
synapse('PLNL', 'SAADL', 5).
synapse('PLNL', 'SMBVL', 1).
synapse('PLNL', 'SMBVL', 5).
synapse('PLNR', 'SAADR', 4).
synapse('PLNR', 'SMBVR', 2).
synapse('PLNR', 'SMBVR', 4).
synapse('PQR', 'AVAL', 3).
synapse('PQR', 'AVAL', 5).
synapse('PQR', 'AVAR', 2).
synapse('PQR', 'AVAR', 9).
synapse('PQR', 'AVDL', 7).
synapse('PQR', 'AVDR', 6).
synapse('PQR', 'AVG', 1).
synapse('PQR', 'LUAR', 1).
synapse('PQR', 'PVNL', 1).
synapse('PQR', 'PVPL', 4).
synapse('PVCL', 'AS1', 1).
synapse('PVCL', 'AVAL', 2).
synapse('PVCL', 'AVAL', 1).
synapse('PVCL', 'AVAL', 1).
synapse('PVCL', 'AVAR', 4).
synapse('PVCL', 'AVBL', 5).
synapse('PVCL', 'AVBR', 1).
synapse('PVCL', 'AVBR', 11).
synapse('PVCL', 'AVDL', 5).
synapse('PVCL', 'AVDR', 2).
synapse('PVCL', 'AVEL', 2).
synapse('PVCL', 'AVER', 1).
synapse('PVCL', 'AVJL', 1).
synapse('PVCL', 'AVJL', 1).
synapse('PVCL', 'AVJL', 2).
synapse('PVCL', 'AVJR', 1).
synapse('PVCL', 'AVJR', 1).
synapse('PVCL', 'DA2', 1).
synapse('PVCL', 'DA5', 1).
synapse('PVCL', 'DA6', 1).
synapse('PVCL', 'DB2', 3).
synapse('PVCL', 'DB3', 4).
synapse('PVCL', 'DB4', 3).
synapse('PVCL', 'DB5', 2).
synapse('PVCL', 'DB6', 2).
synapse('PVCL', 'DB7', 1).
synapse('PVCL', 'DB7', 2).
synapse('PVCL', 'DVA', 1).
synapse('PVCL', 'DVA', 4).
synapse('PVCL', 'PLML', 1).
synapse('PVCL', 'PVCR', 2).
synapse('PVCL', 'PVCR', 5).
synapse('PVCL', 'RID', 1).
synapse('PVCL', 'RID', 4).
synapse('PVCL', 'RIS', 2).
synapse('PVCL', 'SIBVL', 2).
synapse('PVCL', 'VB3', 1).
synapse('PVCL', 'VB4', 1).
synapse('PVCL', 'VB5', 1).
synapse('PVCL', 'VB6', 2).
synapse('PVCL', 'VB8', 1).
synapse('PVCL', 'VB9', 2).
synapse('PVCL', 'VB10', 2).
synapse('PVCL', 'VB10', 1).
synapse('PVCL', 'VB11', 1).
synapse('PVCR', 'AQR', 1).
synapse('PVCR', 'AS2', 1).
synapse('PVCR', 'AVAL', 5).
synapse('PVCR', 'AVAL', 2).
synapse('PVCR', 'AVAL', 5).
synapse('PVCR', 'AVAR', 3).
synapse('PVCR', 'AVAR', 7).
synapse('PVCR', 'AVBL', 2).
synapse('PVCR', 'AVBL', 6).
synapse('PVCR', 'AVBR', 6).
synapse('PVCR', 'AVDL', 5).
synapse('PVCR', 'AVDR', 1).
synapse('PVCR', 'AVEL', 1).
synapse('PVCR', 'AVER', 1).
synapse('PVCR', 'AVJL', 3).
synapse('PVCR', 'AVL', 1).
synapse('PVCR', 'DA9', 1).
synapse('PVCR', 'DB2', 1).
synapse('PVCR', 'DB3', 3).
synapse('PVCR', 'DB4', 4).
synapse('PVCR', 'DB5', 1).
synapse('PVCR', 'DB6', 2).
synapse('PVCR', 'DB7', 1).
synapse('PVCR', 'FLPL', 1).
synapse('PVCR', 'LUAR', 1).
synapse('PVCR', 'PDEL', 1).
synapse('PVCR', 'PDEL', 1).
synapse('PVCR', 'PHCR', 1).
synapse('PVCR', 'PLMR', 1).
synapse('PVCR', 'PVCL', 5).
synapse('PVCR', 'PVCL', 1).
synapse('PVCR', 'PVCL', 2).
synapse('PVCR', 'PVDL', 1).
synapse('PVCR', 'PVR', 1).
synapse('PVCR', 'PVWL', 2).
synapse('PVCR', 'PVWR', 1).
synapse('PVCR', 'PVWR', 1).
synapse('PVCR', 'RID', 2).
synapse('PVCR', 'RID', 3).
synapse('PVCR', 'SIBVR', 2).
synapse('PVCR', 'VA8', 2).
synapse('PVCR', 'VA9', 1).
synapse('PVCR', 'VB4', 3).
synapse('PVCR', 'VB6', 2).
synapse('PVCR', 'VB7', 3).
synapse('PVCR', 'VB8', 1).
synapse('PVCR', 'VB10', 1).
synapse('PVDL', 'AVAL', 6).
synapse('PVDL', 'AVAR', 6).
synapse('PVDL', 'DD5', 1).
synapse('PVDL', 'PVCL', 1).
synapse('PVDL', 'PVCR', 6).
synapse('PVDL', 'VD10', 1).
synapse('PVDR', 'AVAL', 6).
synapse('PVDR', 'AVAR', 9).
synapse('PVDR', 'DVA', 2).
synapse('PVDR', 'DVA', 1).
synapse('PVDR', 'PVCL', 2).
synapse('PVDR', 'PVCL', 11).
synapse('PVDR', 'PVCR', 10).
synapse('PVDR', 'PVDL', 1).
synapse('PVDR', 'VA9', 1).
synapse('PVM', 'AVKL', 7).
synapse('PVM', 'AVKL', 4).
synapse('PVM', 'AVL', 1).
synapse('PVM', 'AVM', 1).
synapse('PVM', 'DVA', 2).
synapse('PVM', 'DVA', 1).
synapse('PVM', 'PDEL', 1).
synapse('PVM', 'PDEL', 1).
synapse('PVM', 'PDEL', 6).
synapse('PVM', 'PDER', 1).
synapse('PVM', 'PDER', 2).
synapse('PVM', 'PDER', 6).
synapse('PVM', 'PVCL', 2).
synapse('PVM', 'PVR', 1).
synapse('PVNL', 'AVAL', 2).
synapse('PVNL', 'AVBR', 2).
synapse('PVNL', 'AVBR', 1).
synapse('PVNL', 'AVDL', 3).
synapse('PVNL', 'AVDR', 3).
synapse('PVNL', 'AVEL', 1).
synapse('PVNL', 'AVFR', 1).
synapse('PVNL', 'AVG', 1).
synapse('PVNL', 'AVJL', 5).
synapse('PVNL', 'AVJR', 2).
synapse('PVNL', 'AVJR', 3).
synapse('PVNL', 'AVL', 2).
synapse('PVNL', 'BDUL', 1).
synapse('PVNL', 'BDUL', 1).
synapse('PVNL', 'BDUR', 2).
synapse('PVNL', 'DD1', 2).
synapse('PVNL', 'MUS', 1).
synapse('PVNL', 'MUS', 2).
synapse('PVNL', 'PQR', 1).
synapse('PVNL', 'PVCL', 1).
synapse('PVNL', 'PVNR', 5).
synapse('PVNL', 'PVQR', 1).
synapse('PVNL', 'PVT', 1).
synapse('PVNL', 'PVWL', 1).
synapse('PVNL', 'RIFL', 1).
synapse('PVNR', 'AVAL', 2).
synapse('PVNR', 'AVAL', 2).
synapse('PVNR', 'AVBL', 1).
synapse('PVNR', 'AVBR', 2).
synapse('PVNR', 'AVDR', 1).
synapse('PVNR', 'AVEL', 2).
synapse('PVNR', 'AVEL', 1).
synapse('PVNR', 'AVJL', 4).
synapse('PVNR', 'AVJR', 1).
synapse('PVNR', 'AVL', 2).
synapse('PVNR', 'BDUL', 1).
synapse('PVNR', 'BDUR', 2).
synapse('PVNR', 'BDUR', 2).
synapse('PVNR', 'DD3', 1).
synapse('PVNR', 'HSNR', 1).
synapse('PVNR', 'HSNR', 1).
synapse('PVNR', 'MUS', 2).
synapse('PVNR', 'MUS', 1).
synapse('PVNR', 'PQR', 2).
synapse('PVNR', 'PVCL', 1).
synapse('PVNR', 'PVNL', 1).
synapse('PVNR', 'PVT', 2).
synapse('PVNR', 'PVWL', 2).
synapse('PVNR', 'VC2', 1).
synapse('PVNR', 'VC2', 1).
synapse('PVNR', 'VC3', 1).
synapse('PVNR', 'VD6', 1).
synapse('PVNR', 'VD7', 1).
synapse('PVNR', 'VD12', 1).
synapse('PVPL', 'ADAL', 1).
synapse('PVPL', 'AQR', 7).
synapse('PVPL', 'AQR', 1).
synapse('PVPL', 'AVAL', 1).
synapse('PVPL', 'AVAL', 1).
synapse('PVPL', 'AVAL', 1).
synapse('PVPL', 'AVAR', 1).
synapse('PVPL', 'AVAR', 1).
synapse('PVPL', 'AVBL', 2).
synapse('PVPL', 'AVBL', 3).
synapse('PVPL', 'AVBR', 6).
synapse('PVPL', 'AVDR', 2).
synapse('PVPL', 'AVER', 1).
synapse('PVPL', 'AVHR', 1).
synapse('PVPL', 'AVKL', 1).
synapse('PVPL', 'AVKR', 6).
synapse('PVPL', 'DVC', 2).
synapse('PVPL', 'PHAR', 3).
synapse('PVPL', 'PQR', 4).
synapse('PVPL', 'PVCR', 1).
synapse('PVPL', 'PVCR', 2).
synapse('PVPL', 'PVPR', 1).
synapse('PVPL', 'PVT', 1).
synapse('PVPL', 'RIGL', 2).
synapse('PVPL', 'VD3', 1).
synapse('PVPL', 'VD13', 2).
synapse('PVPR', 'ADFR', 1).
synapse('PVPR', 'AQR', 9).
synapse('PVPR', 'AQR', 2).
synapse('PVPR', 'ASHR', 1).
synapse('PVPR', 'AVAL', 1).
synapse('PVPR', 'AVAR', 2).
synapse('PVPR', 'AVBL', 4).
synapse('PVPR', 'AVBR', 5).
synapse('PVPR', 'AVHL', 3).
synapse('PVPR', 'AVKL', 1).
synapse('PVPR', 'AVL', 1).
synapse('PVPR', 'AVL', 3).
synapse('PVPR', 'DD2', 1).
synapse('PVPR', 'DVC', 13).
synapse('PVPR', 'DVC', 1).
synapse('PVPR', 'DVC', 1).
synapse('PVPR', 'PVCL', 4).
synapse('PVPR', 'PVCR', 1).
synapse('PVPR', 'PVCR', 6).
synapse('PVPR', 'PVPL', 1).
synapse('PVPR', 'PVQR', 1).
synapse('PVPR', 'RIAR', 2).
synapse('PVPR', 'RIGR', 1).
synapse('PVPR', 'RIMR', 1).
synapse('PVPR', 'RMGR', 1).
synapse('PVPR', 'VD4', 1).
synapse('PVPR', 'VD5', 1).
synapse('PVQL', 'ADAL', 1).
synapse('PVQL', 'AIAL', 3).
synapse('PVQL', 'AIAL', 3).
synapse('PVQL', 'ASJL', 1).
synapse('PVQL', 'ASKL', 5).
synapse('PVQL', 'ASKL', 4).
synapse('PVQL', 'HSNL', 2).
synapse('PVQL', 'PVQR', 2).
synapse('PVQL', 'RMGL', 1).
synapse('PVQR', 'ADAR', 1).
synapse('PVQR', 'AIAR', 3).
synapse('PVQR', 'AIAR', 4).
synapse('PVQR', 'ASER', 1).
synapse('PVQR', 'ASKR', 4).
synapse('PVQR', 'ASKR', 4).
synapse('PVQR', 'AVBL', 1).
synapse('PVQR', 'AVFL', 1).
synapse('PVQR', 'AVFR', 1).
synapse('PVQR', 'AVL', 1).
synapse('PVQR', 'AWAR', 2).
synapse('PVQR', 'DD1', 1).
synapse('PVQR', 'DVC', 1).
synapse('PVQR', 'HSNR', 1).
synapse('PVQR', 'PVNL', 1).
synapse('PVQR', 'PVQL', 2).
synapse('PVQR', 'PVT', 1).
synapse('PVQR', 'RIFR', 1).
synapse('PVQR', 'VD1', 1).
synapse('PVR', 'ADAL', 1).
synapse('PVR', 'ALML', 1).
synapse('PVR', 'AS6', 1).
synapse('PVR', 'AVBL', 4).
synapse('PVR', 'AVBR', 4).
synapse('PVR', 'AVJL', 1).
synapse('PVR', 'AVJL', 2).
synapse('PVR', 'AVJR', 2).
synapse('PVR', 'AVKL', 1).
synapse('PVR', 'DA9', 1).
synapse('PVR', 'DB2', 1).
synapse('PVR', 'DB3', 1).
synapse('PVR', 'DVA', 2).
synapse('PVR', 'DVA', 1).
synapse('PVR', 'IL1DL', 1).
synapse('PVR', 'IL1DR', 1).
synapse('PVR', 'IL1VL', 1).
synapse('PVR', 'IL1VR', 1).
synapse('PVR', 'LUAL', 1).
synapse('PVR', 'LUAR', 1).
synapse('PVR', 'PDEL', 1).
synapse('PVR', 'PDER', 1).
synapse('PVR', 'PLMR', 2).
synapse('PVR', 'PVCR', 1).
synapse('PVR', 'RIPL', 3).
synapse('PVR', 'RIPR', 3).
synapse('PVR', 'SABD', 1).
synapse('PVR', 'URADL', 1).
synapse('PVT', 'AIBL', 1).
synapse('PVT', 'AIBL', 2).
synapse('PVT', 'AIBR', 1).
synapse('PVT', 'AIBR', 4).
synapse('PVT', 'AVKL', 2).
synapse('PVT', 'AVKL', 2).
synapse('PVT', 'AVKL', 5).
synapse('PVT', 'AVKR', 7).
synapse('PVT', 'AVL', 2).
synapse('PVT', 'DVC', 2).
synapse('PVT', 'PVPL', 1).
synapse('PVT', 'RIBL', 1).
synapse('PVT', 'RIBR', 1).
synapse('PVT', 'RIGL', 2).
synapse('PVT', 'RIGR', 3).
synapse('PVT', 'RIH', 1).
synapse('PVT', 'RMEV', 1).
synapse('PVT', 'RMFL', 2).
synapse('PVT', 'RMFR', 1).
synapse('PVT', 'RMFR', 2).
synapse('PVT', 'SMBDR', 1).
synapse('PVWL', 'AVJL', 1).
synapse('PVWL', 'PVCR', 2).
synapse('PVWL', 'PVT', 2).
synapse('PVWL', 'PVWR', 1).
synapse('PVWL', 'VA12', 1).
synapse('PVWR', 'AVAR', 1).
synapse('PVWR', 'AVDR', 1).
synapse('PVWR', 'PVCR', 1).
synapse('PVWR', 'PVCR', 1).
synapse('PVWR', 'PVT', 1).
synapse('PVWR', 'VA12', 1).
synapse('RIAL', 'CEPVL', 1).
synapse('RIAL', 'RIAR', 1).
synapse('RIAL', 'RIVL', 2).
synapse('RIAL', 'RIVR', 1).
synapse('RIAL', 'RIVR', 3).
synapse('RIAL', 'RMDDL', 2).
synapse('RIAL', 'RMDDL', 10).
synapse('RIAL', 'RMDDR', 7).
synapse('RIAL', 'RMDL', 4).
synapse('RIAL', 'RMDL', 2).
synapse('RIAL', 'RMDR', 4).
synapse('RIAL', 'RMDR', 2).
synapse('RIAL', 'RMDVL', 1).
synapse('RIAL', 'RMDVL', 8).
synapse('RIAL', 'RMDVR', 2).
synapse('RIAL', 'RMDVR', 9).
synapse('RIAL', 'SIADL', 2).
synapse('RIAL', 'SMDDL', 3).
synapse('RIAL', 'SMDDL', 5).
synapse('RIAL', 'SMDDR', 3).
synapse('RIAL', 'SMDDR', 7).
synapse('RIAL', 'SMDVL', 1).
synapse('RIAL', 'SMDVL', 5).
synapse('RIAL', 'SMDVR', 1).
synapse('RIAL', 'SMDVR', 10).
synapse('RIAR', 'CEPVR', 1).
synapse('RIAR', 'IL1R', 1).
synapse('RIAR', 'RIAL', 4).
synapse('RIAR', 'RIVL', 1).
synapse('RIAR', 'RMDDL', 1).
synapse('RIAR', 'RMDDL', 9).
synapse('RIAR', 'RMDDR', 1).
synapse('RIAR', 'RMDDR', 10).
synapse('RIAR', 'RMDL', 2).
synapse('RIAR', 'RMDL', 1).
synapse('RIAR', 'RMDR', 1).
synapse('RIAR', 'RMDR', 7).
synapse('RIAR', 'RMDVL', 12).
synapse('RIAR', 'RMDVR', 1).
synapse('RIAR', 'RMDVR', 9).
synapse('RIAR', 'SAADR', 1).
synapse('RIAR', 'SIADL', 1).
synapse('RIAR', 'SIADR', 1).
synapse('RIAR', 'SIAVL', 1).
synapse('RIAR', 'SMDDL', 2).
synapse('RIAR', 'SMDDL', 5).
synapse('RIAR', 'SMDDR', 1).
synapse('RIAR', 'SMDDR', 6).
synapse('RIAR', 'SMDVL', 2).
synapse('RIAR', 'SMDVL', 11).
synapse('RIAR', 'SMDVR', 1).
synapse('RIAR', 'SMDVR', 6).
synapse('RIBL', 'AIBR', 2).
synapse('RIBL', 'AUAL', 1).
synapse('RIBL', 'AVAL', 1).
synapse('RIBL', 'AVAL', 1).
synapse('RIBL', 'AVBL', 1).
synapse('RIBL', 'AVBR', 1).
synapse('RIBL', 'AVBR', 1).
synapse('RIBL', 'AVDR', 1).
synapse('RIBL', 'AVEL', 1).
synapse('RIBL', 'AVEL', 1).
synapse('RIBL', 'AVER', 3).
synapse('RIBL', 'AVER', 2).
synapse('RIBL', 'BAGR', 1).
synapse('RIBL', 'OLQDL', 2).
synapse('RIBL', 'OLQVL', 1).
synapse('RIBL', 'PVT', 1).
synapse('RIBL', 'RIAL', 1).
synapse('RIBL', 'RIAL', 2).
synapse('RIBL', 'RIBL', 1).
synapse('RIBL', 'RIBR', 3).
synapse('RIBL', 'RIGL', 1).
synapse('RIBL', 'SIADL', 1).
synapse('RIBL', 'SIAVL', 1).
synapse('RIBL', 'SIBDL', 1).
synapse('RIBL', 'SIBVL', 1).
synapse('RIBL', 'SIBVR', 1).
synapse('RIBL', 'SMBDL', 1).
synapse('RIBL', 'SMDDL', 1).
synapse('RIBL', 'SMDVR', 2).
synapse('RIBL', 'SMDVR', 2).
synapse('RIBR', 'AIBL', 1).
synapse('RIBR', 'AIBL', 1).
synapse('RIBR', 'AIZR', 1).
synapse('RIBR', 'AVAR', 2).
synapse('RIBR', 'AVBL', 1).
synapse('RIBR', 'AVBR', 1).
synapse('RIBR', 'AVEL', 2).
synapse('RIBR', 'AVEL', 1).
synapse('RIBR', 'AVER', 1).
synapse('RIBR', 'AVER', 1).
synapse('RIBR', 'BAGL', 1).
synapse('RIBR', 'BAGL', 1).
synapse('RIBR', 'OLQDR', 2).
synapse('RIBR', 'OLQVR', 1).
synapse('RIBR', 'PVT', 1).
synapse('RIBR', 'RIAR', 2).
synapse('RIBR', 'RIBL', 3).
synapse('RIBR', 'RIBR', 1).
synapse('RIBR', 'RIGR', 1).
synapse('RIBR', 'RIGR', 1).
synapse('RIBR', 'RIH', 1).
synapse('RIBR', 'SIADR', 1).
synapse('RIBR', 'SIAVR', 1).
synapse('RIBR', 'SIBDR', 1).
synapse('RIBR', 'SIBVR', 1).
synapse('RIBR', 'SMBDR', 1).
synapse('RIBR', 'SMDDL', 1).
synapse('RIBR', 'SMDDL', 1).
synapse('RIBR', 'SMDDR', 1).
synapse('RIBR', 'SMDVL', 2).
synapse('RICL', 'ADAR', 1).
synapse('RICL', 'ASHL', 2).
synapse('RICL', 'AVAL', 5).
synapse('RICL', 'AVAR', 6).
synapse('RICL', 'AVKL', 1).
synapse('RICL', 'AVKR', 1).
synapse('RICL', 'AVKR', 1).
synapse('RICL', 'AWBR', 1).
synapse('RICL', 'RIML', 1).
synapse('RICL', 'RIMR', 1).
synapse('RICL', 'RIMR', 2).
synapse('RICL', 'RIVR', 1).
synapse('RICL', 'RMFR', 1).
synapse('RICL', 'SMBDL', 2).
synapse('RICL', 'SMDDL', 3).
synapse('RICL', 'SMDDR', 3).
synapse('RICL', 'SMDVR', 1).
synapse('RICR', 'ADAR', 1).
synapse('RICR', 'ASHR', 2).
synapse('RICR', 'AVAL', 5).
synapse('RICR', 'AVAR', 5).
synapse('RICR', 'AVKL', 1).
synapse('RICR', 'SMBDR', 1).
synapse('RICR', 'SMDDL', 4).
synapse('RICR', 'SMDDR', 3).
synapse('RICR', 'SMDVL', 2).
synapse('RICR', 'SMDVR', 1).
synapse('RID', 'ALA', 1).
synapse('RID', 'AS2', 1).
synapse('RID', 'AVBL', 1).
synapse('RID', 'AVBR', 2).
synapse('RID', 'DA6', 1).
synapse('RID', 'DA6', 2).
synapse('RID', 'DA9', 1).
synapse('RID', 'DB1', 1).
synapse('RID', 'DD1', 3).
synapse('RID', 'DD1', 1).
synapse('RID', 'DD2', 3).
synapse('RID', 'DD2', 1).
synapse('RID', 'DD3', 1).
synapse('RID', 'DD3', 2).
synapse('RID', 'MUS', 2).
synapse('RID', 'MUS', 1).
synapse('RID', 'PDB', 2).
synapse('RID', 'VD5', 1).
synapse('RID', 'VD5', 1).
synapse('RID', 'VD13', 1).
synapse('RIFL', 'ALML', 2).
synapse('RIFL', 'AVBL', 10).
synapse('RIFL', 'AVBR', 1).
synapse('RIFL', 'AVG', 1).
synapse('RIFL', 'AVHR', 1).
synapse('RIFL', 'AVJR', 2).
synapse('RIFL', 'PVPL', 3).
synapse('RIFL', 'RIML', 4).
synapse('RIFL', 'VD1', 1).
synapse('RIFR', 'ASHR', 2).
synapse('RIFR', 'AVBL', 1).
synapse('RIFR', 'AVBR', 3).
synapse('RIFR', 'AVBR', 14).
synapse('RIFR', 'AVFL', 1).
synapse('RIFR', 'AVG', 1).
synapse('RIFR', 'AVHL', 1).
synapse('RIFR', 'AVJL', 1).
synapse('RIFR', 'AVJR', 2).
synapse('RIFR', 'HSNR', 1).
synapse('RIFR', 'PVCL', 1).
synapse('RIFR', 'PVCR', 1).
synapse('RIFR', 'PVPR', 4).
synapse('RIFR', 'RIMR', 4).
synapse('RIFR', 'RIPR', 1).
synapse('RIGL', 'AIBR', 3).
synapse('RIGL', 'AIZR', 1).
synapse('RIGL', 'ALNL', 1).
synapse('RIGL', 'AQR', 2).
synapse('RIGL', 'AVEL', 1).
synapse('RIGL', 'AVEL', 1).
synapse('RIGL', 'AVER', 1).
synapse('RIGL', 'AVKL', 1).
synapse('RIGL', 'AVKR', 2).
synapse('RIGL', 'BAGR', 1).
synapse('RIGL', 'BAGR', 1).
synapse('RIGL', 'DVC', 1).
synapse('RIGL', 'OLLL', 1).
synapse('RIGL', 'OLQDL', 1).
synapse('RIGL', 'OLQVL', 1).
synapse('RIGL', 'RIBL', 1).
synapse('RIGL', 'RIBL', 1).
synapse('RIGL', 'RIGR', 3).
synapse('RIGL', 'RIR', 2).
synapse('RIGL', 'RMEL', 1).
synapse('RIGL', 'RMFL', 1).
synapse('RIGL', 'RMHR', 3).
synapse('RIGL', 'URYDL', 1).
synapse('RIGL', 'URYVL', 1).
synapse('RIGL', 'VB2', 1).
synapse('RIGL', 'VD1', 2).
synapse('RIGR', 'AIBL', 3).
synapse('RIGR', 'ALNR', 1).
synapse('RIGR', 'AQR', 1).
synapse('RIGR', 'AVER', 2).
synapse('RIGR', 'AVKL', 4).
synapse('RIGR', 'AVKR', 1).
synapse('RIGR', 'AVKR', 1).
synapse('RIGR', 'BAGL', 1).
synapse('RIGR', 'OLLR', 1).
synapse('RIGR', 'OLQDR', 1).
synapse('RIGR', 'OLQVR', 1).
synapse('RIGR', 'RIBR', 1).
synapse('RIGR', 'RIBR', 1).
synapse('RIGR', 'RIGL', 3).
synapse('RIGR', 'RIR', 1).
synapse('RIGR', 'RMHL', 4).
synapse('RIGR', 'URYDR', 1).
synapse('RIGR', 'URYVR', 1).
synapse('RIH', 'ADFR', 1).
synapse('RIH', 'AIZL', 4).
synapse('RIH', 'AIZR', 4).
synapse('RIH', 'AUAR', 1).
synapse('RIH', 'BAGR', 1).
synapse('RIH', 'CEPDL', 1).
synapse('RIH', 'CEPDL', 1).
synapse('RIH', 'CEPDR', 1).
synapse('RIH', 'CEPDR', 1).
synapse('RIH', 'CEPVL', 1).
synapse('RIH', 'CEPVL', 1).
synapse('RIH', 'CEPVR', 1).
synapse('RIH', 'CEPVR', 1).
synapse('RIH', 'CEPVR', 1).
synapse('RIH', 'FLPL', 1).
synapse('RIH', 'IL2L', 2).
synapse('RIH', 'IL2R', 1).
synapse('RIH', 'OLQDL', 2).
synapse('RIH', 'OLQDL', 2).
synapse('RIH', 'OLQDR', 1).
synapse('RIH', 'OLQDR', 2).
synapse('RIH', 'OLQVL', 1).
synapse('RIH', 'OLQVR', 6).
synapse('RIH', 'RIAL', 1).
synapse('RIH', 'RIAL', 10).
synapse('RIH', 'RIAR', 8).
synapse('RIH', 'RIBL', 5).
synapse('RIH', 'RIBR', 4).
synapse('RIH', 'RIPL', 4).
synapse('RIH', 'RIPL', 1).
synapse('RIH', 'RIPR', 3).
synapse('RIH', 'RIPR', 3).
synapse('RIH', 'RMER', 2).
synapse('RIH', 'RMEV', 1).
synapse('RIH', 'URYVR', 1).
synapse('RIML', 'AIBR', 1).
synapse('RIML', 'AIYL', 1).
synapse('RIML', 'AVAL', 1).
synapse('RIML', 'AVAR', 2).
synapse('RIML', 'AVBL', 2).
synapse('RIML', 'AVBR', 3).
synapse('RIML', 'AVEL', 2).
synapse('RIML', 'AVER', 3).
synapse('RIML', 'MUS', 3).
synapse('RIML', 'MUS', 1).
synapse('RIML', 'RIBL', 1).
synapse('RIML', 'RIS', 1).
synapse('RIML', 'RMDL', 1).
synapse('RIML', 'RMDR', 1).
synapse('RIML', 'RMFR', 1).
synapse('RIML', 'SAADR', 1).
synapse('RIML', 'SAAVL', 3).
synapse('RIML', 'SAAVR', 2).
synapse('RIML', 'SMDDR', 1).
synapse('RIML', 'SMDDR', 4).
synapse('RIML', 'SMDVL', 1).
synapse('RIMR', 'ADAR', 1).
synapse('RIMR', 'AIBL', 1).
synapse('RIMR', 'AIBL', 4).
synapse('RIMR', 'AIYR', 1).
synapse('RIMR', 'AVAL', 3).
synapse('RIMR', 'AVAL', 2).
synapse('RIMR', 'AVAR', 1).
synapse('RIMR', 'AVBL', 2).
synapse('RIMR', 'AVBR', 1).
synapse('RIMR', 'AVBR', 4).
synapse('RIMR', 'AVEL', 3).
synapse('RIMR', 'AVER', 2).
synapse('RIMR', 'AVJL', 1).
synapse('RIMR', 'AVKL', 1).
synapse('RIMR', 'MUS', 3).
synapse('RIMR', 'MUS', 1).
synapse('RIMR', 'RIBR', 1).
synapse('RIMR', 'RIS', 1).
synapse('RIMR', 'RIS', 1).
synapse('RIMR', 'RMDL', 2).
synapse('RIMR', 'RMDL', 1).
synapse('RIMR', 'RMDR', 1).
synapse('RIMR', 'RMFL', 1).
synapse('RIMR', 'RMFR', 1).
synapse('RIMR', 'SAAVL', 1).
synapse('RIMR', 'SAAVL', 2).
synapse('RIMR', 'SAAVR', 3).
synapse('RIMR', 'SMDDL', 2).
synapse('RIMR', 'SMDDR', 4).
synapse('RIPL', 'OLQDL', 1).
synapse('RIPL', 'OLQDR', 1).
synapse('RIPL', 'RMED', 1).
synapse('RIPR', 'OLQDL', 1).
synapse('RIPR', 'OLQDR', 1).
synapse('RIPR', 'RMED', 1).
synapse('RIR', 'AFDR', 1).
synapse('RIR', 'AIZL', 3).
synapse('RIR', 'AIZL', 3).
synapse('RIR', 'AIZR', 4).
synapse('RIR', 'AIZR', 1).
synapse('RIR', 'AUAL', 1).
synapse('RIR', 'AWBR', 1).
synapse('RIR', 'BAGL', 1).
synapse('RIR', 'BAGR', 1).
synapse('RIR', 'BAGR', 1).
synapse('RIR', 'DVA', 2).
synapse('RIR', 'HSNL', 1).
synapse('RIR', 'PVPL', 1).
synapse('RIR', 'RIAL', 1).
synapse('RIR', 'RIAL', 4).
synapse('RIR', 'RIAR', 1).
synapse('RIR', 'RIGL', 1).
synapse('RIR', 'URXL', 5).
synapse('RIR', 'URXR', 1).
synapse('RIR', 'URXR', 1).
synapse('RIS', 'AIBR', 1).
synapse('RIS', 'AVEL', 7).
synapse('RIS', 'AVER', 7).
synapse('RIS', 'AVJL', 1).
synapse('RIS', 'AVKL', 1).
synapse('RIS', 'AVKR', 4).
synapse('RIS', 'AVL', 2).
synapse('RIS', 'CEPDR', 1).
synapse('RIS', 'CEPVL', 2).
synapse('RIS', 'CEPVR', 1).
synapse('RIS', 'DB1', 1).
synapse('RIS', 'OLLR', 1).
synapse('RIS', 'RIBL', 3).
synapse('RIS', 'RIBR', 5).
synapse('RIS', 'RIML', 1).
synapse('RIS', 'RIML', 1).
synapse('RIS', 'RIMR', 1).
synapse('RIS', 'RIMR', 1).
synapse('RIS', 'RIMR', 3).
synapse('RIS', 'RMDDL', 1).
synapse('RIS', 'RMDL', 2).
synapse('RIS', 'RMDR', 1).
synapse('RIS', 'RMDR', 3).
synapse('RIS', 'SMDDL', 1).
synapse('RIS', 'SMDDR', 2).
synapse('RIS', 'SMDDR', 1).
synapse('RIS', 'SMDVL', 1).
synapse('RIS', 'SMDVR', 1).
synapse('RIS', 'URYVR', 1).
synapse('RIVL', 'AIBL', 1).
synapse('RIVL', 'MUS', 4).
synapse('RIVL', 'RIAL', 1).
synapse('RIVL', 'RIAR', 1).
synapse('RIVL', 'RIVR', 2).
synapse('RIVL', 'RMDL', 2).
synapse('RIVL', 'SAADR', 3).
synapse('RIVL', 'SDQR', 2).
synapse('RIVL', 'SIAVR', 2).
synapse('RIVL', 'SMDDR', 1).
synapse('RIVL', 'SMDVL', 1).
synapse('RIVR', 'AIBR', 1).
synapse('RIVR', 'MUS', 3).
synapse('RIVR', 'MUS', 2).
synapse('RIVR', 'RIAL', 2).
synapse('RIVR', 'RIAR', 1).
synapse('RIVR', 'RIAR', 1).
synapse('RIVR', 'RIVL', 2).
synapse('RIVR', 'RMDDL', 1).
synapse('RIVR', 'RMDR', 1).
synapse('RIVR', 'RMDVR', 1).
synapse('RIVR', 'RMEV', 1).
synapse('RIVR', 'SAADL', 2).
synapse('RIVR', 'SDQR', 2).
synapse('RIVR', 'SIAVL', 2).
synapse('RIVR', 'SMDDL', 2).
synapse('RIVR', 'SMDVR', 2).
synapse('RIVR', 'SMDVR', 2).
synapse('RMDDL', 'MUS', 1).
synapse('RMDDL', 'MUS', 7).
synapse('RMDDL', 'OLQVL', 1).
synapse('RMDDL', 'RMDL', 1).
synapse('RMDDL', 'RMDVL', 1).
synapse('RMDDL', 'RMDVR', 7).
synapse('RMDDL', 'SMDDL', 1).
synapse('RMDDR', 'MUS', 10).
synapse('RMDDR', 'OLQVR', 1).
synapse('RMDDR', 'RMDVL', 1).
synapse('RMDDR', 'RMDVL', 11).
synapse('RMDDR', 'RMDVR', 1).
synapse('RMDDR', 'SAADR', 1).
synapse('RMDDR', 'SMDDR', 1).
synapse('RMDDR', 'URYDL', 1).
synapse('RMDL', 'MUS', 9).
synapse('RMDL', 'MUS', 2).
synapse('RMDL', 'OLLR', 2).
synapse('RMDL', 'RIAL', 4).
synapse('RMDL', 'RIAR', 3).
synapse('RMDL', 'RMDDL', 1).
synapse('RMDL', 'RMDDR', 1).
synapse('RMDL', 'RMDR', 3).
synapse('RMDL', 'RMDVL', 1).
synapse('RMDL', 'RMER', 1).
synapse('RMDL', 'RMFL', 1).
synapse('RMDR', 'AVKL', 1).
synapse('RMDR', 'MUS', 3).
synapse('RMDR', 'MUS', 1).
synapse('RMDR', 'RIAL', 3).
synapse('RMDR', 'RIAR', 3).
synapse('RMDR', 'RIAR', 4).
synapse('RMDR', 'RIMR', 2).
synapse('RMDR', 'RIS', 1).
synapse('RMDR', 'RMDDL', 1).
synapse('RMDR', 'RMDL', 1).
synapse('RMDR', 'RMDVR', 1).
synapse('RMDVL', 'AVER', 1).
synapse('RMDVL', 'MUS', 3).
synapse('RMDVL', 'MUS', 6).
synapse('RMDVL', 'OLQDL', 1).
synapse('RMDVL', 'RMDDL', 1).
synapse('RMDVL', 'RMDDR', 6).
synapse('RMDVL', 'RMDL', 1).
synapse('RMDVL', 'RMDVR', 1).
synapse('RMDVL', 'SAAVL', 1).
synapse('RMDVL', 'SMDVL', 1).
synapse('RMDVR', 'AVEL', 1).
synapse('RMDVR', 'AVER', 1).
synapse('RMDVR', 'MUS', 6).
synapse('RMDVR', 'MUS', 3).
synapse('RMDVR', 'OLQDR', 1).
synapse('RMDVR', 'RMDDL', 1).
synapse('RMDVR', 'RMDDL', 3).
synapse('RMDVR', 'RMDDR', 1).
synapse('RMDVR', 'RMDR', 1).
synapse('RMDVR', 'RMDVL', 1).
synapse('RMDVR', 'SAAVR', 1).
synapse('RMDVR', 'SIBDR', 1).
synapse('RMDVR', 'SIBVR', 1).
synapse('RMDVR', 'SMDVR', 1).
synapse('RMED', 'IL1VL', 1).
synapse('RMED', 'MUS', 10).
synapse('RMED', 'RIBL', 1).
synapse('RMED', 'RIBR', 1).
synapse('RMED', 'RIPL', 1).
synapse('RMED', 'RIPR', 1).
synapse('RMED', 'RMEV', 2).
synapse('RMEL', 'MUS', 12).
synapse('RMEL', 'RIGL', 1).
synapse('RMEL', 'RMEV', 1).
synapse('RMER', 'MUS', 15).
synapse('RMER', 'RMEV', 1).
synapse('RMEV', 'AVEL', 1).
synapse('RMEV', 'AVER', 1).
synapse('RMEV', 'IL1DL', 1).
synapse('RMEV', 'IL1DR', 1).
synapse('RMEV', 'MUS', 5).
synapse('RMEV', 'RMED', 2).
synapse('RMEV', 'RMEL', 1).
synapse('RMEV', 'RMER', 1).
synapse('RMEV', 'SMDDR', 1).
synapse('RMFL', 'AVKL', 4).
synapse('RMFL', 'AVKR', 4).
synapse('RMFL', 'MUS', 2).
synapse('RMFL', 'MUS', 1).
synapse('RMFL', 'PVT', 1).
synapse('RMFL', 'RIGR', 1).
synapse('RMFL', 'RMDR', 3).
synapse('RMFL', 'RMGR', 1).
synapse('RMFL', 'URBR', 1).
synapse('RMFR', 'AVKL', 3).
synapse('RMFR', 'AVKR', 3).
synapse('RMFR', 'RMDL', 2).
synapse('RMGL', 'ADAL', 1).
synapse('RMGL', 'ADLL', 1).
synapse('RMGL', 'AIBR', 1).
synapse('RMGL', 'ALML', 1).
synapse('RMGL', 'ALNL', 1).
synapse('RMGL', 'ASHL', 1).
synapse('RMGL', 'ASHL', 1).
synapse('RMGL', 'ASKL', 1).
synapse('RMGL', 'AVAL', 1).
synapse('RMGL', 'AVBR', 2).
synapse('RMGL', 'AVEL', 2).
synapse('RMGL', 'AWBL', 1).
synapse('RMGL', 'CEPDL', 1).
synapse('RMGL', 'IL2L', 1).
synapse('RMGL', 'MUS', 3).
synapse('RMGL', 'MUS', 1).
synapse('RMGL', 'RID', 1).
synapse('RMGL', 'RMDL', 1).
synapse('RMGL', 'RMDR', 1).
synapse('RMGL', 'RMDR', 2).
synapse('RMGL', 'RMDVL', 3).
synapse('RMGL', 'RMHL', 3).
synapse('RMGL', 'RMHR', 1).
synapse('RMGL', 'SIAVL', 1).
synapse('RMGL', 'SIBVL', 2).
synapse('RMGL', 'SIBVR', 1).
synapse('RMGL', 'SMBVL', 1).
synapse('RMGL', 'SMBVL', 1).
synapse('RMGL', 'URXL', 1).
synapse('RMGL', 'URXL', 1).
synapse('RMGR', 'ADAR', 1).
synapse('RMGR', 'AIMR', 1).
synapse('RMGR', 'ALNR', 1).
synapse('RMGR', 'ASHR', 1).
synapse('RMGR', 'ASHR', 1).
synapse('RMGR', 'ASKR', 1).
synapse('RMGR', 'AVAR', 1).
synapse('RMGR', 'AVBR', 1).
synapse('RMGR', 'AVDL', 1).
synapse('RMGR', 'AVER', 3).
synapse('RMGR', 'AVJL', 1).
synapse('RMGR', 'AWBR', 1).
synapse('RMGR', 'IL2R', 1).
synapse('RMGR', 'MUS', 3).
synapse('RMGR', 'RIR', 1).
synapse('RMGR', 'RMDL', 4).
synapse('RMGR', 'RMDR', 2).
synapse('RMGR', 'RMDVR', 5).
synapse('RMGR', 'RMHR', 1).
synapse('RMGR', 'URXR', 1).
synapse('RMGR', 'URXR', 1).
synapse('RMHL', 'MUS', 7).
synapse('RMHL', 'MUS', 1).
synapse('RMHL', 'RMDR', 1).
synapse('RMHL', 'RMGL', 3).
synapse('RMHL', 'SIBVR', 1).
synapse('RMHR', 'MUS', 5).
synapse('RMHR', 'MUS', 2).
synapse('RMHR', 'RMER', 1).
synapse('RMHR', 'RMGL', 1).
synapse('RMHR', 'RMGR', 1).
synapse('SAADL', 'AIBL', 1).
synapse('SAADL', 'AVAL', 6).
synapse('SAADL', 'RIML', 1).
synapse('SAADL', 'RIML', 2).
synapse('SAADL', 'RIMR', 1).
synapse('SAADL', 'RIMR', 5).
synapse('SAADL', 'RMGR', 1).
synapse('SAADL', 'SMBDL', 1).
synapse('SAADR', 'AIBR', 1).
synapse('SAADR', 'AVAR', 3).
synapse('SAADR', 'OLLL', 1).
synapse('SAADR', 'RIML', 1).
synapse('SAADR', 'RIML', 3).
synapse('SAADR', 'RIMR', 2).
synapse('SAADR', 'RIMR', 3).
synapse('SAADR', 'RMDDR', 1).
synapse('SAADR', 'RMFL', 1).
synapse('SAADR', 'RMGL', 1).
synapse('SAAVL', 'AIBL', 1).
synapse('SAAVL', 'ALNL', 1).
synapse('SAAVL', 'AVAL', 1).
synapse('SAAVL', 'AVAL', 16).
synapse('SAAVL', 'OLLR', 1).
synapse('SAAVL', 'RIML', 2).
synapse('SAAVL', 'RIMR', 12).
synapse('SAAVL', 'RMDVL', 1).
synapse('SAAVL', 'RMFR', 2).
synapse('SAAVL', 'SMBVR', 3).
synapse('SAAVL', 'SMDDR', 8).
synapse('SAAVR', 'AVAR', 4).
synapse('SAAVR', 'AVAR', 9).
synapse('SAAVR', 'RIML', 5).
synapse('SAAVR', 'RIMR', 2).
synapse('SAAVR', 'RMDVR', 1).
synapse('SAAVR', 'SMBVL', 2).
synapse('SAAVR', 'SMDDL', 6).
synapse('SABD', 'AVAL', 4).
synapse('SABD', 'VA2', 1).
synapse('SABD', 'VA2', 3).
synapse('SABD', 'VA3', 2).
synapse('SABD', 'VA4', 1).
synapse('SABVL', 'AVAR', 3).
synapse('SABVL', 'DA1', 2).
synapse('SABVL', 'DA2', 1).
synapse('SABVR', 'AVAL', 1).
synapse('SABVR', 'AVAR', 1).
synapse('SABVR', 'DA1', 3).
synapse('SDQL', 'AIBR', 1).
synapse('SDQL', 'ALML', 1).
synapse('SDQL', 'AVAL', 1).
synapse('SDQL', 'AVAL', 1).
synapse('SDQL', 'AVAR', 3).
synapse('SDQL', 'AVEL', 1).
synapse('SDQL', 'FLPL', 1).
synapse('SDQL', 'RICR', 1).
synapse('SDQL', 'RIS', 2).
synapse('SDQL', 'RIS', 1).
synapse('SDQL', 'RMFL', 1).
synapse('SDQL', 'SDQR', 1).
synapse('SDQR', 'ADLL', 1).
synapse('SDQR', 'AIBL', 2).
synapse('SDQR', 'AVAL', 1).
synapse('SDQR', 'AVAL', 2).
synapse('SDQR', 'AVBL', 1).
synapse('SDQR', 'AVBL', 2).
synapse('SDQR', 'AVBL', 4).
synapse('SDQR', 'AVBR', 4).
synapse('SDQR', 'DVA', 3).
synapse('SDQR', 'RICR', 1).
synapse('SDQR', 'RIVL', 2).
synapse('SDQR', 'RIVR', 2).
synapse('SDQR', 'RMHL', 2).
synapse('SDQR', 'RMHR', 1).
synapse('SDQR', 'SDQL', 1).
synapse('SDQR', 'SIBVL', 1).
synapse('SIADL', 'RIBL', 1).
synapse('SIADR', 'RIBR', 1).
synapse('SIAVL', 'RIBL', 1).
synapse('SIAVR', 'RIBR', 1).
synapse('SIBDL', 'RIBL', 1).
synapse('SIBDL', 'SIBVL', 1).
synapse('SIBDR', 'AIML', 1).
synapse('SIBDR', 'RIBR', 1).
synapse('SIBDR', 'SIBVR', 1).
synapse('SIBVL', 'AVBL', 1).
synapse('SIBVL', 'AVBR', 1).
synapse('SIBVL', 'RIBL', 1).
synapse('SIBVL', 'SDQR', 1).
synapse('SIBVL', 'SIBDL', 1).
synapse('SIBVR', 'RIBL', 1).
synapse('SIBVR', 'RIBR', 1).
synapse('SIBVR', 'RMHL', 1).
synapse('SIBVR', 'SIBDR', 1).
synapse('SMBDL', 'AVAR', 1).
synapse('SMBDL', 'AVKL', 1).
synapse('SMBDL', 'AVKR', 1).
synapse('SMBDL', 'MUS', 3).
synapse('SMBDL', 'MUS', 5).
synapse('SMBDL', 'RIBL', 1).
synapse('SMBDL', 'RMED', 3).
synapse('SMBDL', 'SAADL', 1).
synapse('SMBDL', 'SAAVR', 1).
synapse('SMBDL', 'SAAVR', 1).
synapse('SMBDR', 'ALNL', 1).
synapse('SMBDR', 'AVAL', 1).
synapse('SMBDR', 'AVKL', 1).
synapse('SMBDR', 'AVKR', 2).
synapse('SMBDR', 'MUS', 3).
synapse('SMBDR', 'MUS', 7).
synapse('SMBDR', 'RIBR', 1).
synapse('SMBDR', 'RMED', 4).
synapse('SMBDR', 'SAAVL', 3).
synapse('SMBVL', 'MUS', 3).
synapse('SMBVL', 'MUS', 3).
synapse('SMBVL', 'PLNL', 1).
synapse('SMBVL', 'RMEV', 1).
synapse('SMBVL', 'RMEV', 4).
synapse('SMBVL', 'SAADL', 3).
synapse('SMBVL', 'SAAVR', 2).
synapse('SMBVR', 'AVKL', 1).
synapse('SMBVR', 'AVKR', 1).
synapse('SMBVR', 'MUS', 3).
synapse('SMBVR', 'MUS', 3).
synapse('SMBVR', 'RMEV', 3).
synapse('SMBVR', 'SAADR', 4).
synapse('SMBVR', 'SAAVL', 3).
synapse('SMDDL', 'MUS', 4).
synapse('SMDDL', 'MUS', 1).
synapse('SMDDL', 'RIAL', 1).
synapse('SMDDL', 'RIAR', 1).
synapse('SMDDL', 'RIAR', 1).
synapse('SMDDL', 'RIBL', 1).
synapse('SMDDL', 'RIBR', 1).
synapse('SMDDL', 'RIS', 1).
synapse('SMDDL', 'RMDDL', 1).
synapse('SMDDL', 'SMDVR', 2).
synapse('SMDDR', 'MUS', 3).
synapse('SMDDR', 'RIAL', 2).
synapse('SMDDR', 'RIAR', 1).
synapse('SMDDR', 'RIBR', 1).
synapse('SMDDR', 'RIS', 1).
synapse('SMDDR', 'RMDDR', 1).
synapse('SMDDR', 'VD1', 1).
synapse('SMDVL', 'MUS', 3).
synapse('SMDVL', 'PVR', 1).
synapse('SMDVL', 'RIAL', 3).
synapse('SMDVL', 'RIAR', 8).
synapse('SMDVL', 'RIBR', 2).
synapse('SMDVL', 'RIS', 1).
synapse('SMDVL', 'RIVL', 1).
synapse('SMDVL', 'RIVL', 1).
synapse('SMDVL', 'RMDDR', 1).
synapse('SMDVL', 'RMDVL', 1).
synapse('SMDVL', 'SMDDR', 4).
synapse('SMDVL', 'SMDVR', 1).
synapse('SMDVR', 'MUS', 3).
synapse('SMDVR', 'MUS', 1).
synapse('SMDVR', 'RIAL', 7).
synapse('SMDVR', 'RIAR', 5).
synapse('SMDVR', 'RIBL', 2).
synapse('SMDVR', 'RIVR', 2).
synapse('SMDVR', 'RIVR', 1).
synapse('SMDVR', 'RMDDL', 1).
synapse('SMDVR', 'RMDDL', 1).
synapse('SMDVR', 'RMDVR', 1).
synapse('SMDVR', 'SMDDL', 2).
synapse('SMDVR', 'SMDVL', 1).
synapse('SMDVR', 'VB1', 1).
synapse('URADL', 'IL1DL', 2).
synapse('URADL', 'MUS', 1).
synapse('URADL', 'MUS', 5).
synapse('URADL', 'RIPL', 3).
synapse('URADL', 'RMEL', 1).
synapse('URADR', 'IL1DR', 1).
synapse('URADR', 'MUS', 2).
synapse('URADR', 'MUS', 5).
synapse('URADR', 'RIPR', 3).
synapse('URADR', 'RMDVR', 1).
synapse('URADR', 'RMED', 1).
synapse('URADR', 'RMER', 1).
synapse('URADR', 'URYDR', 1).
synapse('URAVL', 'MUS', 6).
synapse('URAVL', 'MUS', 3).
synapse('URAVL', 'RIPL', 3).
synapse('URAVL', 'RMEL', 1).
synapse('URAVL', 'RMER', 1).
synapse('URAVL', 'RMEV', 2).
synapse('URAVR', 'IL1R', 1).
synapse('URAVR', 'MUS', 1).
synapse('URAVR', 'MUS', 7).
synapse('URAVR', 'RIPR', 3).
synapse('URAVR', 'RMDVL', 1).
synapse('URAVR', 'RMER', 2).
synapse('URAVR', 'RMEV', 2).
synapse('URBL', 'AVBL', 1).
synapse('URBL', 'CEPDL', 1).
synapse('URBL', 'IL1L', 1).
synapse('URBL', 'OLQDL', 1).
synapse('URBL', 'OLQVL', 1).
synapse('URBL', 'RICR', 1).
synapse('URBL', 'RMDDR', 1).
synapse('URBL', 'SIAVL', 1).
synapse('URBL', 'SMBDR', 1).
synapse('URBL', 'URXL', 2).
synapse('URBL', 'URXL', 2).
synapse('URBR', 'ADAR', 1).
synapse('URBR', 'AVBR', 1).
synapse('URBR', 'CEPDR', 1).
synapse('URBR', 'IL1R', 3).
synapse('URBR', 'IL2R', 1).
synapse('URBR', 'OLQDR', 1).
synapse('URBR', 'OLQVR', 1).
synapse('URBR', 'RICR', 1).
synapse('URBR', 'RMDL', 1).
synapse('URBR', 'RMDR', 1).
synapse('URBR', 'RMFL', 1).
synapse('URBR', 'SIAVR', 2).
synapse('URBR', 'SMBDL', 1).
synapse('URBR', 'URXR', 2).
synapse('URBR', 'URXR', 4).
synapse('URXL', 'ASHL', 1).
synapse('URXL', 'AUAL', 1).
synapse('URXL', 'AUAL', 4).
synapse('URXL', 'AVBL', 1).
synapse('URXL', 'AVEL', 3).
synapse('URXL', 'AVEL', 1).
synapse('URXL', 'AVJR', 1).
synapse('URXL', 'RIAL', 1).
synapse('URXL', 'RIAL', 7).
synapse('URXL', 'RICL', 1).
synapse('URXL', 'RIGL', 2).
synapse('URXL', 'RIGL', 1).
synapse('URXL', 'RMGL', 1).
synapse('URXL', 'RMGL', 2).
synapse('URXR', 'AUAR', 1).
synapse('URXR', 'AUAR', 3).
synapse('URXR', 'AVBL', 1).
synapse('URXR', 'AVBR', 2).
synapse('URXR', 'AVER', 2).
synapse('URXR', 'IL2R', 1).
synapse('URXR', 'OLQVR', 1).
synapse('URXR', 'RIAR', 3).
synapse('URXR', 'RIGR', 2).
synapse('URXR', 'RIPR', 3).
synapse('URXR', 'RMDR', 1).
synapse('URXR', 'RMGR', 1).
synapse('URXR', 'RMGR', 1).
synapse('URXR', 'SIAVR', 1).
synapse('URYDL', 'AVAL', 1).
synapse('URYDL', 'AVER', 2).
synapse('URYDL', 'RIBL', 1).
synapse('URYDL', 'RIGL', 1).
synapse('URYDL', 'RMDDR', 1).
synapse('URYDL', 'RMDDR', 3).
synapse('URYDL', 'RMDVL', 2).
synapse('URYDL', 'RMDVL', 4).
synapse('URYDL', 'SMDDL', 1).
synapse('URYDL', 'SMDDR', 1).
synapse('URYDL', 'SMDDR', 1).
synapse('URYDR', 'AVAR', 1).
synapse('URYDR', 'AVEL', 2).
synapse('URYDR', 'AVER', 2).
synapse('URYDR', 'RIBR', 1).
synapse('URYDR', 'RIGR', 1).
synapse('URYDR', 'RMDDL', 3).
synapse('URYDR', 'RMDVR', 1).
synapse('URYDR', 'RMDVR', 4).
synapse('URYDR', 'SMDDL', 3).
synapse('URYDR', 'SMDDL', 1).
synapse('URYVL', 'AVAR', 1).
synapse('URYVL', 'AVBR', 1).
synapse('URYVL', 'AVER', 5).
synapse('URYVL', 'IL1VL', 1).
synapse('URYVL', 'RIAL', 1).
synapse('URYVL', 'RIBL', 2).
synapse('URYVL', 'RIGL', 1).
synapse('URYVL', 'RIH', 1).
synapse('URYVL', 'RIS', 1).
synapse('URYVL', 'RMDDL', 4).
synapse('URYVL', 'RMDVR', 2).
synapse('URYVL', 'SIBVR', 1).
synapse('URYVL', 'SMDVR', 1).
synapse('URYVL', 'SMDVR', 3).
synapse('URYVR', 'AVAL', 1).
synapse('URYVR', 'AVAL', 1).
synapse('URYVR', 'AVEL', 6).
synapse('URYVR', 'IL1VR', 1).
synapse('URYVR', 'RIAR', 1).
synapse('URYVR', 'RIBR', 1).
synapse('URYVR', 'RIGR', 1).
synapse('URYVR', 'RMDDR', 6).
synapse('URYVR', 'RMDVL', 1).
synapse('URYVR', 'RMDVL', 3).
synapse('URYVR', 'SIBDR', 1).
synapse('URYVR', 'SIBVL', 1).
synapse('URYVR', 'SMDVL', 3).
synapse('VA1', 'AVAL', 3).
synapse('VA1', 'DA2', 2).
synapse('VA1', 'DD1', 9).
synapse('VA1', 'MUS', 11).
synapse('VA1', 'VD1', 2).
synapse('VA2', 'AVAL', 4).
synapse('VA2', 'AVAL', 1).
synapse('VA2', 'DD1', 13).
synapse('VA2', 'MUS', 19).
synapse('VA2', 'SABD', 3).
synapse('VA2', 'VA3', 2).
synapse('VA2', 'VB1', 2).
synapse('VA2', 'VD1', 2).
synapse('VA2', 'VD1', 1).
synapse('VA2', 'VD2', 8).
synapse('VA2', 'VD2', 3).
synapse('VA3', 'AS1', 1).
synapse('VA3', 'AVAL', 1).
synapse('VA3', 'AVAR', 2).
synapse('VA3', 'DD1', 18).
synapse('VA3', 'DD2', 11).
synapse('VA3', 'MUS', 29).
synapse('VA3', 'SABD', 2).
synapse('VA3', 'VA4', 1).
synapse('VA3', 'VD2', 3).
synapse('VA3', 'VD3', 3).
synapse('VA4', 'AS2', 2).
synapse('VA4', 'AVAL', 1).
synapse('VA4', 'AVAR', 3).
synapse('VA4', 'AVDL', 1).
synapse('VA4', 'DA5', 1).
synapse('VA4', 'DD2', 21).
synapse('VA4', 'MUS', 25).
synapse('VA4', 'SABD', 1).
synapse('VA4', 'VB3', 2).
synapse('VA4', 'VD4', 3).
synapse('VA5', 'AS3', 2).
synapse('VA5', 'AVAL', 5).
synapse('VA5', 'AVAR', 3).
synapse('VA5', 'DA5', 2).
synapse('VA5', 'DD2', 5).
synapse('VA5', 'DD3', 13).
synapse('VA5', 'MUS', 19).
synapse('VA5', 'VD5', 2).
synapse('VA6', 'AVAL', 6).
synapse('VA6', 'AVAR', 2).
synapse('VA6', 'DD3', 24).
synapse('VA6', 'MUS', 20).
synapse('VA6', 'VB5', 2).
synapse('VA6', 'VD5', 1).
synapse('VA6', 'VD6', 2).
synapse('VA7', 'AS5', 1).
synapse('VA7', 'AVAL', 2).
synapse('VA7', 'AVAR', 4).
synapse('VA7', 'DD3', 3).
synapse('VA7', 'DD4', 12).
synapse('VA7', 'MUS', 27).
synapse('VA7', 'VB3', 1).
synapse('VA7', 'VD7', 9).
synapse('VA8', 'AS6', 1).
synapse('VA8', 'AVAL', 10).
synapse('VA8', 'AVAR', 4).
synapse('VA8', 'AVBR', 1).
synapse('VA8', 'DD4', 21).
synapse('VA8', 'MUS', 23).
synapse('VA8', 'PDER', 1).
synapse('VA8', 'PVCR', 2).
synapse('VA8', 'VA8', 1).
synapse('VA8', 'VA9', 1).
synapse('VA8', 'VB6', 1).
synapse('VA8', 'VB8', 1).
synapse('VA8', 'VB8', 3).
synapse('VA8', 'VB9', 3).
synapse('VA8', 'VD7', 5).
synapse('VA8', 'VD8', 5).
synapse('VA8', 'VD8', 1).
synapse('VA9', 'AVAL', 1).
synapse('VA9', 'AVBR', 1).
synapse('VA9', 'DD4', 3).
synapse('VA9', 'DD5', 15).
synapse('VA9', 'DVB', 1).
synapse('VA9', 'DVC', 1).
synapse('VA9', 'MUS', 20).
synapse('VA9', 'PVCR', 1).
synapse('VA9', 'PVT', 1).
synapse('VA9', 'VB8', 6).
synapse('VA9', 'VB8', 1).
synapse('VA9', 'VB9', 4).
synapse('VA9', 'VD7', 1).
synapse('VA9', 'VD9', 10).
synapse('VA10', 'AVAL', 1).
synapse('VA10', 'AVAR', 1).
synapse('VA11', 'AVAL', 1).
synapse('VA11', 'AVAR', 7).
synapse('VA11', 'DD6', 10).
synapse('VA11', 'MUS', 18).
synapse('VA11', 'PVNR', 2).
synapse('VA11', 'VB10', 1).
synapse('VA11', 'VD12', 4).
synapse('VA12', 'AS11', 2).
synapse('VA12', 'AVAR', 1).
synapse('VA12', 'DA8', 3).
synapse('VA12', 'DA9', 5).
synapse('VA12', 'DB7', 4).
synapse('VA12', 'DD6', 2).
synapse('VA12', 'LUAL', 2).
synapse('VA12', 'MUS', 14).
synapse('VA12', 'PHCL', 1).
synapse('VA12', 'PHCR', 1).
synapse('VA12', 'PVCL', 2).
synapse('VA12', 'PVCR', 3).
synapse('VA12', 'VA11', 1).
synapse('VA12', 'VB11', 1).
synapse('VA12', 'VD12', 3).
synapse('VA12', 'VD13', 11).
synapse('VB1', 'AIBR', 1).
synapse('VB1', 'AVBL', 1).
synapse('VB1', 'AVKL', 4).
synapse('VB1', 'DB2', 2).
synapse('VB1', 'DD1', 1).
synapse('VB1', 'DVA', 1).
synapse('VB1', 'MUS', 5).
synapse('VB1', 'RIML', 2).
synapse('VB1', 'RMFL', 2).
synapse('VB1', 'SAADL', 7).
synapse('VB1', 'SAADL', 2).
synapse('VB1', 'SAADR', 2).
synapse('VB1', 'SAADR', 2).
synapse('VB1', 'SABD', 1).
synapse('VB1', 'SMDVR', 1).
synapse('VB1', 'VA1', 3).
synapse('VB1', 'VA3', 1).
synapse('VB1', 'VB2', 4).
synapse('VB1', 'VD1', 3).
synapse('VB1', 'VD2', 1).
synapse('VB2', 'AVBL', 3).
synapse('VB2', 'AVBR', 1).
synapse('VB2', 'DB4', 1).
synapse('VB2', 'DD1', 20).
synapse('VB2', 'DD2', 1).
synapse('VB2', 'MUS', 26).
synapse('VB2', 'RIGL', 1).
synapse('VB2', 'VA2', 1).
synapse('VB2', 'VB1', 4).
synapse('VB2', 'VB3', 1).
synapse('VB2', 'VB5', 1).
synapse('VB2', 'VB7', 2).
synapse('VB2', 'VC2', 1).
synapse('VB2', 'VD2', 9).
synapse('VB2', 'VD3', 3).
synapse('VB3', 'AVBR', 1).
synapse('VB3', 'DB1', 1).
synapse('VB3', 'DD2', 37).
synapse('VB3', 'MUS', 35).
synapse('VB3', 'VA4', 1).
synapse('VB3', 'VA7', 1).
synapse('VB3', 'VB2', 1).
synapse('VB4', 'AVBL', 1).
synapse('VB4', 'AVBR', 1).
synapse('VB4', 'DB1', 1).
synapse('VB4', 'DB4', 1).
synapse('VB4', 'DD2', 6).
synapse('VB4', 'DD3', 16).
synapse('VB4', 'MUS', 20).
synapse('VB4', 'VB5', 1).
synapse('VB5', 'AVBL', 1).
synapse('VB5', 'DD3', 27).
synapse('VB5', 'MUS', 22).
synapse('VB5', 'VB2', 1).
synapse('VB5', 'VB4', 1).
synapse('VB5', 'VB6', 1).
synapse('VB5', 'VD6', 7).
synapse('VB6', 'AVBL', 1).
synapse('VB6', 'AVBR', 2).
synapse('VB6', 'DA4', 1).
synapse('VB6', 'DD4', 30).
synapse('VB6', 'MUS', 28).
synapse('VB6', 'VA8', 1).
synapse('VB6', 'VB5', 1).
synapse('VB6', 'VB7', 1).
synapse('VB6', 'VD6', 1).
synapse('VB6', 'VD7', 8).
synapse('VB7', 'AVBL', 2).
synapse('VB7', 'AVBR', 2).
synapse('VB7', 'DD4', 2).
synapse('VB7', 'MUS', 2).
synapse('VB7', 'VB2', 2).
synapse('VB8', 'AVBL', 7).
synapse('VB8', 'AVBR', 3).
synapse('VB8', 'DD5', 30).
synapse('VB8', 'MUS', 32).
synapse('VB8', 'VA8', 3).
synapse('VB8', 'VA9', 1).
synapse('VB8', 'VA9', 9).
synapse('VB8', 'VB9', 3).
synapse('VB8', 'VB9', 3).
synapse('VB8', 'VD9', 10).
synapse('VB8', 'VD10', 1).
synapse('VB9', 'AVAL', 5).
synapse('VB9', 'AVAR', 4).
synapse('VB9', 'AVBL', 1).
synapse('VB9', 'AVBR', 6).
synapse('VB9', 'DD5', 8).
synapse('VB9', 'DVB', 1).
synapse('VB9', 'MUS', 24).
synapse('VB9', 'PVCL', 2).
synapse('VB9', 'VA8', 3).
synapse('VB9', 'VA9', 4).
synapse('VB9', 'VB8', 3).
synapse('VB9', 'VB8', 1).
synapse('VB9', 'VD10', 5).
synapse('VB10', 'AVBL', 2).
synapse('VB10', 'AVBR', 1).
synapse('VB10', 'AVKL', 1).
synapse('VB10', 'DD6', 9).
synapse('VB10', 'MUS', 20).
synapse('VB10', 'PVCL', 1).
synapse('VB10', 'PVT', 1).
synapse('VB10', 'VD11', 1).
synapse('VB10', 'VD12', 2).
synapse('VB11', 'AVBL', 2).
synapse('VB11', 'AVBR', 1).
synapse('VB11', 'DD6', 7).
synapse('VB11', 'MUS', 14).
synapse('VB11', 'PVCR', 1).
synapse('VB11', 'VA12', 1).
synapse('VB11', 'VA12', 1).
synapse('VC1', 'AVL', 2).
synapse('VC1', 'DD1', 7).
synapse('VC1', 'DD2', 6).
synapse('VC1', 'DD3', 6).
synapse('VC1', 'DVC', 1).
synapse('VC1', 'MUS', 1).
synapse('VC1', 'MUS', 5).
synapse('VC1', 'PVT', 2).
synapse('VC1', 'VC2', 3).
synapse('VC1', 'VC2', 6).
synapse('VC1', 'VC3', 1).
synapse('VC1', 'VC3', 2).
synapse('VC1', 'VD1', 4).
synapse('VC1', 'VD1', 1).
synapse('VC1', 'VD2', 1).
synapse('VC1', 'VD3', 1).
synapse('VC1', 'VD4', 2).
synapse('VC1', 'VD5', 5).
synapse('VC1', 'VD6', 1).
synapse('VC2', 'DB4', 1).
synapse('VC2', 'DD1', 6).
synapse('VC2', 'DD2', 4).
synapse('VC2', 'DD3', 9).
synapse('VC2', 'DVC', 1).
synapse('VC2', 'MUS', 9).
synapse('VC2', 'MUS', 1).
synapse('VC2', 'PVCR', 1).
synapse('VC2', 'PVQR', 1).
synapse('VC2', 'PVT', 2).
synapse('VC2', 'VC1', 6).
synapse('VC2', 'VC1', 4).
synapse('VC2', 'VC3', 4).
synapse('VC2', 'VC3', 2).
synapse('VC2', 'VD1', 2).
synapse('VC2', 'VD2', 2).
synapse('VC2', 'VD4', 5).
synapse('VC2', 'VD5', 5).
synapse('VC2', 'VD6', 1).
synapse('VC3', 'AVL', 1).
synapse('VC3', 'DD1', 2).
synapse('VC3', 'DD2', 4).
synapse('VC3', 'DD3', 5).
synapse('VC3', 'DD4', 1).
synapse('VC3', 'DD4', 12).
synapse('VC3', 'DVC', 1).
synapse('VC3', 'HSNR', 1).
synapse('VC3', 'MUS', 3).
synapse('VC3', 'MUS', 8).
synapse('VC3', 'PVNR', 1).
synapse('VC3', 'PVPR', 1).
synapse('VC3', 'PVQR', 4).
synapse('VC3', 'VC1', 2).
synapse('VC3', 'VC1', 2).
synapse('VC3', 'VC2', 2).
synapse('VC3', 'VC2', 1).
synapse('VC3', 'VC4', 1).
synapse('VC3', 'VC5', 2).
synapse('VC3', 'VD1', 1).
synapse('VC3', 'VD2', 1).
synapse('VC3', 'VD3', 1).
synapse('VC3', 'VD4', 2).
synapse('VC3', 'VD5', 4).
synapse('VC3', 'VD6', 4).
synapse('VC3', 'VD7', 5).
synapse('VC4', 'AVBL', 1).
synapse('VC4', 'AVFR', 1).
synapse('VC4', 'AVHR', 1).
synapse('VC4', 'MUS', 4).
synapse('VC4', 'MUS', 3).
synapse('VC4', 'VC1', 1).
synapse('VC4', 'VC3', 1).
synapse('VC4', 'VC3', 4).
synapse('VC4', 'VC5', 1).
synapse('VC4', 'VC5', 1).
synapse('VC5', 'AVFL', 1).
synapse('VC5', 'AVFR', 1).
synapse('VC5', 'DVC', 2).
synapse('VC5', 'HSNL', 1).
synapse('VC5', 'MUS', 2).
synapse('VC5', 'OLLR', 1).
synapse('VC5', 'PVT', 1).
synapse('VC5', 'URBL', 3).
synapse('VC5', 'VC3', 2).
synapse('VC5', 'VC3', 1).
synapse('VC5', 'VC4', 1).
synapse('VC5', 'VC4', 1).
synapse('VC6', 'MUS', 1).
synapse('VD1', 'DD1', 4).
synapse('VD1', 'DD1', 1).
synapse('VD1', 'DVC', 5).
synapse('VD1', 'MUS', 12).
synapse('VD1', 'RIFL', 1).
synapse('VD1', 'RIGL', 2).
synapse('VD1', 'SMDDR', 1).
synapse('VD1', 'VA1', 2).
synapse('VD1', 'VA2', 1).
synapse('VD1', 'VC1', 1).
synapse('VD1', 'VD2', 7).
synapse('VD2', 'AS1', 1).
synapse('VD2', 'DD1', 2).
synapse('VD2', 'DD1', 1).
synapse('VD2', 'MUS', 22).
synapse('VD2', 'VA2', 3).
synapse('VD2', 'VA2', 6).
synapse('VD2', 'VB2', 3).
synapse('VD2', 'VD1', 7).
synapse('VD2', 'VD3', 2).
synapse('VD3', 'MUS', 23).
synapse('VD3', 'PVPL', 1).
synapse('VD3', 'VA3', 2).
synapse('VD3', 'VB2', 2).
synapse('VD3', 'VD2', 2).
synapse('VD3', 'VD4', 1).
synapse('VD4', 'DD2', 2).
synapse('VD4', 'MUS', 25).
synapse('VD4', 'PVPR', 1).
synapse('VD4', 'VD3', 1).
synapse('VD4', 'VD5', 1).
synapse('VD5', 'AVAR', 1).
synapse('VD5', 'MUS', 26).
synapse('VD5', 'PVPR', 1).
synapse('VD5', 'VA5', 2).
synapse('VD5', 'VB4', 2).
synapse('VD5', 'VD4', 1).
synapse('VD5', 'VD6', 2).
synapse('VD6', 'AVAL', 1).
synapse('VD6', 'MUS', 27).
synapse('VD6', 'VA6', 1).
synapse('VD6', 'VB5', 2).
synapse('VD6', 'VD5', 2).
synapse('VD6', 'VD7', 1).
synapse('VD7', 'MUS', 24).
synapse('VD7', 'VA9', 1).
synapse('VD7', 'VD6', 1).
synapse('VD8', 'DD4', 1).
synapse('VD8', 'DD4', 1).
synapse('VD8', 'MUS', 25).
synapse('VD8', 'VA8', 1).
synapse('VD8', 'VA8', 4).
synapse('VD9', 'MUS', 28).
synapse('VD9', 'PDER', 1).
synapse('VD9', 'VD10', 5).
synapse('VD10', 'AVBR', 1).
synapse('VD10', 'DD5', 1).
synapse('VD10', 'DD5', 1).
synapse('VD10', 'DVC', 4).
synapse('VD10', 'MUS', 22).
synapse('VD10', 'VB9', 2).
synapse('VD10', 'VD9', 5).
synapse('VD11', 'AVAR', 2).
synapse('VD11', 'MUS', 11).
synapse('VD11', 'VA11', 1).
synapse('VD11', 'VB10', 1).
synapse('VD12', 'MUS', 13).
synapse('VD12', 'VA11', 3).
synapse('VD12', 'VA12', 2).
synapse('VD12', 'VB10', 1).
synapse('VD12', 'VB11', 1).
synapse('VD13', 'AVAR', 2).
synapse('VD13', 'MUS', 12).
synapse('VD13', 'PVCL', 1).
synapse('VD13', 'PVCR', 1).
synapse('VD13', 'PVPL', 2).
synapse('VD13', 'VA12', 1).
synapse('I1L', 'I1R', 1).
synapse('I1L', 'I3', 1).
synapse('I1L', 'I5', 1).
synapse('I1L', 'RIPL', 1).
synapse('I1L', 'RIPR', 1).
synapse('I1R', 'I1L', 1).
synapse('I1R', 'I3', 1).
synapse('I1R', 'I5', 1).
synapse('I1R', 'RIPL', 1).
synapse('I1R', 'RIPR', 1).
synapse('I2L', 'I1L', 1).
synapse('I2L', 'I1R', 1).
synapse('I2L', 'M1', 2).
synapse('I2L', 'M1', 1).
synapse('I2R', 'I1L', 1).
synapse('I2R', 'I1R', 1).
synapse('I2R', 'M1', 2).
synapse('I2R', 'M1', 1).
synapse('I3', 'M1', 2).
synapse('I3', 'M2L', 1).
synapse('I3', 'M2L', 1).
synapse('I3', 'M2R', 1).
synapse('I3', 'M2R', 1).
synapse('I4', 'I2L', 5).
synapse('I4', 'I2R', 5).
synapse('I4', 'I5', 2).
synapse('I4', 'M1', 2).
synapse('I5', 'I1L', 3).
synapse('I5', 'I1L', 1).
synapse('I5', 'I1R', 2).
synapse('I5', 'I1R', 1).
synapse('I5', 'M1', 1).
synapse('I5', 'M5', 1).
synapse('I5', 'M5', 1).
synapse('I5', 'MI', 2).
synapse('I6', 'I2L', 2).
synapse('I6', 'I2R', 2).
synapse('I6', 'I3', 1).
synapse('I6', 'M4', 1).
synapse('I6', 'M5', 2).
synapse('I6', 'NSML', 2).
synapse('I6', 'NSMR', 2).
synapse('M1', 'I2L', 2).
synapse('M1', 'I2R', 2).
synapse('M1', 'I3', 1).
synapse('M1', 'I4', 1).
synapse('M2L', 'I1E', 3).
synapse('M2L', 'I1L', 3).
synapse('M2L', 'I3', 2).
synapse('M2L', 'I3', 1).
synapse('M2L', 'M2R', 1).
synapse('M2L', 'M5', 1).
synapse('M2L', 'MI', 2).
synapse('M2R', 'I1L', 3).
synapse('M2R', 'I1R', 3).
synapse('M2R', 'I3', 2).
synapse('M2R', 'I3', 1).
synapse('M2R', 'M3L', 1).
synapse('M2R', 'M3R', 1).
synapse('M2R', 'M5', 1).
synapse('M2R', 'MI', 2).
synapse('M2R', 'MI', 1).
synapse('M3L', 'I1L', 4).
synapse('M3L', 'I1R', 4).
synapse('M3L', 'I4', 2).
synapse('M3L', 'I5', 3).
synapse('M3L', 'I6', 1).
synapse('M3L', 'M1', 1).
synapse('M3L', 'M3R', 1).
synapse('M3L', 'MCL', 1).
synapse('M3L', 'MCR', 1).
synapse('M3L', 'MI', 1).
synapse('M3L', 'NSML', 2).
synapse('M3L', 'NSMR', 3).
synapse('M3R', 'I1L', 4).
synapse('M3R', 'I1R', 4).
synapse('M3R', 'I3', 2).
synapse('M3R', 'I4', 6).
synapse('M3R', 'I5', 3).
synapse('M3R', 'I6', 1).
synapse('M3R', 'M1', 1).
synapse('M3R', 'M3L', 1).
synapse('M3R', 'MCL', 1).
synapse('M3R', 'MCR', 1).
synapse('M3R', 'MI', 1).
synapse('M3R', 'NSML', 2).
synapse('M3R', 'NSMR', 3).
synapse('M4', 'I3', 1).
synapse('M4', 'I5', 13).
synapse('M4', 'I6', 2).
synapse('M4', 'I6', 1).
synapse('M4', 'M2L', 1).
synapse('M4', 'M2R', 1).
synapse('M4', 'M4', 6).
synapse('M4', 'M5', 1).
synapse('M4', 'NSML', 1).
synapse('M4', 'NSMR', 1).
synapse('M5', 'I5', 3).
synapse('M5', 'I5', 1).
synapse('M5', 'I6', 1).
synapse('M5', 'M1', 1).
synapse('M5', 'M2L', 2).
synapse('M5', 'M2R', 2).
synapse('M5', 'M5', 4).
synapse('MCL', 'I1L', 3).
synapse('MCL', 'I1R', 3).
synapse('MCL', 'I2L', 1).
synapse('MCL', 'I2R', 1).
synapse('MCL', 'I3', 1).
synapse('MCL', 'M1', 1).
synapse('MCL', 'M2L', 2).
synapse('MCL', 'M2R', 2).
synapse('MCR', 'I1L', 3).
synapse('MCR', 'I1R', 3).
synapse('MCR', 'I3', 1).
synapse('MCR', 'M1', 1).
synapse('MCR', 'M2L', 2).
synapse('MCR', 'M2R', 2).
synapse('MI', 'I1L', 1).
synapse('MI', 'I1R', 1).
synapse('MI', 'I3', 1).
synapse('MI', 'I4', 1).
synapse('MI', 'I5', 2).
synapse('MI', 'M1', 1).
synapse('MI', 'M2L', 2).
synapse('MI', 'M2R', 2).
synapse('MI', 'M3L', 1).
synapse('MI', 'M3R', 1).
synapse('MI', 'MCL', 2).
synapse('MI', 'MCR', 2).
synapse('NSML', 'I1L', 1).
synapse('NSML', 'I1R', 2).
synapse('NSML', 'I2L', 6).
synapse('NSML', 'I2R', 6).
synapse('NSML', 'I3', 2).
synapse('NSML', 'I4', 3).
synapse('NSML', 'I5', 2).
synapse('NSML', 'I6', 2).
synapse('NSML', 'M3L', 1).
synapse('NSML', 'M3R', 1).
synapse('NSMR', 'I1L', 2).
synapse('NSMR', 'I1R', 2).
synapse('NSMR', 'I2L', 6).
synapse('NSMR', 'I2R', 6).
synapse('NSMR', 'I3', 2).
synapse('NSMR', 'I4', 3).
synapse('NSMR', 'I5', 2).
synapse('NSMR', 'I6', 2).
synapse('NSMR', 'M3L', 1).
synapse('NSMR', 'M3R', 1).

/*
neuron(1, 'ADAL', 'Glutamate', ['null']).
neuron(2, 'ADAR', 'Glutamate', ['null']).
neuron(3, 'ADEL', 'Dopamine', ['DOP#2', 'EXP#1']).
neuron(4, 'ADER', 'Dopamine', ['DOP#2', 'EXP#1']).
neuron(5, 'ADFL', 'Serotonin', ['OSM#9', 'OCR#2', 'SRB#6']).
neuron(6, 'ADFR', 'Serotonin', ['OSM#9 ', 'OCR#2', 'SRB#6']).
neuron(7, 'ADLL', 'FMRFamide', ['OSM#9', 'OCR#1', 'OCR#2', 'SRE#1', 'SRB#6']).
neuron(8, 'ADLR', 'FMRFamide', ['OSM#9', 'OCR#1', 'OCR#2', 'SRE#1', 'SRB#6']).
neuron(9, 'AFDL', 'Glutamate', ['GCY#12']).
neuron(10, 'AFDR', 'Glutamate', ['GCY#12']).
neuron(11, 'AIAL', 'Acetylcholine', ['GLR#2', 'SRA#11']).
neuron(12, 'AIAR', 'Acetylcholine', ['GLR#2', 'SRA#11']).
neuron(13, 'AIBL', 'Glutamate', ['GLR#1', 'GLR#2', 'GLR#5', 'GGR#1']).
neuron(14, 'AIBR', 'Glutamate', ['GLR#1', 'GLR#2', 'GLR#5', 'GGR#1']).
neuron(15, 'AIML', 'Serotonin', ['null']).
neuron(16, 'AIMR', 'Serotonin', ['null']).
neuron(17, 'AINL', 'Glutamate', ['null']).
neuron(18, 'AINR', 'Glutamate', ['null']).
neuron(19, 'AIYL', 'Acetylcholine', ['SER#2', 'SRA#11']).
neuron(20, 'AIYR', 'Acetylcholine', ['SER#2', 'SRA#11']).
neuron(21, 'AIZL', 'Glutamate', ['SER#2']).
neuron(22, 'AIZR', 'Glutamate', ['SER#2']).
neuron(23, 'ALA', 'Glutamate', ['SRA#10']).
neuron(24, 'ALML', 'Glutamate', ['MEC#2', 'MEC#4', 'MEC#10', 'MEC#9', 'MEC#6', 'DEG#3', 'DES#2', 'GLR#8', 'DOP#1']).
neuron(25, 'ALMR', 'Glutamate', ['MEC#2', 'MEC#4', 'MEC#10', 'MEC#9', 'MEC#6', 'DEG#3', 'DES#2', 'GLR#8', 'DOP#1']).
neuron(26, 'ALNL', 'Acetylcholine', ['SER#2', 'DOP#1', 'GCY#35']).
neuron(27, 'ALNR', 'Acetylcholine', ['SER#2', 'DOP#1', 'GCY#35']).
neuron(28, 'AQR', 'Glutamate', ['GCY#32', 'NPR#1', 'GCY#35']).
neuron(29, 'AS1', 'Acetylcholine', ['null']).
neuron(30, 'AS10', 'Acetylcholine', ['null']).
neuron(31, 'AS11', 'Acetylcholine', ['null']).
neuron(32, 'AS2', 'Acetylcholine', ['null']).
neuron(33, 'AS3', 'Acetylcholine', ['null']).
neuron(34, 'AS4', 'Acetylcholine', ['null']).
neuron(35, 'AS5', 'Acetylcholine', ['null']).
neuron(36, 'AS6', 'Acetylcholine', ['null']).
neuron(37, 'AS7', 'Acetylcholine', ['null']).
neuron(38, 'AS8', 'Acetylcholine', ['null']).
neuron(39, 'AS9', 'Acetylcholine', ['null']).
neuron(40, 'ASEL', 'FMRFamide', ['GCY#6', 'GCY#7', 'OSM#9', 'GCY#12', 'DOP#3']).
neuron(41, 'ASER', 'FMRFamide', ['GCY#5', 'OSM#9', 'GCY#12', 'DOP#3']).
neuron(42, 'ASGL', 'Glutamate', ['OSM#9', 'NPR#1']).
neuron(43, 'ASGR', 'Glutamate', ['NPR#1', 'OSM#9']).
neuron(44, 'ASHL', 'Glutamate', ['OSM#9', 'OCR#2', 'SRA#6', 'SRB#6', 'NPR#1', 'UNC#8']).
neuron(45, 'ASHR', 'Glutamate', ['OSM#9', 'OCR#2', 'SRA#6', 'SRB#6', 'NPR#1', 'UNC#8']).
neuron(46, 'ASIL', 'null', ['SRD#1', 'STR#2', 'STR#3', 'DAF#11', 'SRA#6']).
neuron(47, 'ASIR', 'null', ['SRD#1', 'STR#2', 'STR#3', 'DAF#11', 'SRA#6']).
neuron(48, 'ASJL', 'Glutamate', ['OSM#9', 'SRE#1', 'DAF#11']).
neuron(49, 'ASJR', 'Glutamate', ['OSM#9', 'SRE#1', 'DAF#11']).
neuron(50, 'ASKL', 'Glutamate', ['OSM#9', 'SRA#7', 'SRA#9', 'SRG#2', 'SRG#8', 'DAF#11']).
neuron(51, 'ASKR', 'Glutamate', ['OSM#9', 'SRA#7', 'SRA#9', 'SRG#2', 'SRG#8', 'DAF#11']).
neuron(52, 'AUAL', 'Glutamate', ['GLR#4', 'NPR#1', 'SER#2', 'DOP#1', 'SER#2']).
neuron(53, 'AUAR', 'Glutamate', ['GLR#4', 'NPR#1', 'SER#2', 'DOP#1', 'SER#2']).
neuron(54, 'AVAL', 'FMRFamide', ['GLR#1', 'GLR#2', 'GLR#4', 'GLR#5', 'NMR#1', 'GGR#3', 'GGR#2']).
neuron(55, 'AVAR', 'FMRFamide', ['GLR#1', 'GLR#2', 'GLR#4', 'GLR#5', 'NMR#1', 'GGR#3', 'GGR#2']).
neuron(56, 'AVBL', 'Glutamate', ['GLR#1', 'GLR#5', 'SRA#11', 'GGR#3', 'UNC#8', 'GGR#3']).
neuron(57, 'AVBR', 'Glutamate', ['GLR#1', 'GLR#5', 'SRA#11', 'GGR#3', 'UNC#8', 'GGR#3']).
neuron(58, 'AVDL', 'Glutamate', ['GLR#1', 'GLR#2', 'GLR#5', 'NMR#1', 'NMR#2', 'UNC#8']).
neuron(59, 'AVDR', 'Glutamate', ['GLR#1', 'GLR#2', 'GLR#5', 'NMR#1', 'NMR#2', 'UNC#8']).
neuron(60, 'AVEL', 'FMRFamide', ['GLR#1', 'GLR#2', 'GLR#5', 'NMR#1', 'NMR#2']).
neuron(61, 'AVER', 'FMRFamide', ['GLR#1', 'GLR#2', 'GLR#5', 'NMR#1', 'NMR#2']).
neuron(62, 'AVFL', 'Glutamate', ['null']).
neuron(63, 'AVFR', 'Glutamate', ['null']).
neuron(64, 'AVG', 'Glutamate', ['GLR#1', 'GLR#2', 'NMR#1', 'NMR#2', 'DEG#3']).
neuron(65, 'AVHL', 'Glutamate', ['GLR#4', 'SER#2', 'GGR#1']).
neuron(66, 'AVHR', 'Glutamate', ['GLR#4', 'SER#2', 'GGR#1']).
neuron(67, 'AVJL', 'Glutamate', ['GLR#1']).
neuron(68, 'AVJR', 'Glutamate', ['GLR#1']).
neuron(69, 'AVKL', 'FMRFamide', ['GLR#5']).
neuron(70, 'AVKR', 'FMRFamide', ['GLR#5']).
neuron(71, 'AVL', 'GABA', ['null']).
neuron(72, 'AVM', 'Glutamate', ['MEC#2', 'MEC#4', 'MEC#10', 'MEC#9', 'MEC#6', 'DOP#1', 'GCY#35']).
neuron(73, 'AWAL', 'null', ['ODR#10', 'OSM#9', 'OCR#1', 'OCR#2']).
neuron(74, 'AWAR', 'null', ['ODR#10', 'OSM#9', 'OCR#1', 'OCR#2']).
neuron(75, 'AWBL', 'Glutamate', ['STR#1', 'DAF#11', 'AEX#2']).
neuron(76, 'AWBR', 'Glutamate', ['STR#1', 'DAF#11', 'AEX#2']).
neuron(77, 'AWCL', 'Glutamate', ['OSM#9', 'DAF#11', 'STR#2', 'GCY#12']).
neuron(78, 'AWCR', 'Glutamate', ['OSM#9', 'DAF#11', 'STR#2', 'GCY#12']).
neuron(79, 'BAGL', 'Glutamate', ['GCY#33']).
neuron(80, 'BAGR', 'Glutamate', ['GCY#33']).
neuron(81, 'BDUL', 'GABA', ['GLR#8']).
neuron(82, 'BDUR', 'GABA', ['GLR#8', 'SER#2', 'GCY#35']).
neuron(83, 'CANL*', 'Monoamine', ['SER#2', 'GGR#2']).
neuron(84, 'CANR*', 'Monoamine', ['SER#2', 'GGR#2']).
neuron(85, 'CEPDL', 'Dopamine', ['DOP#2']).
neuron(86, 'CEPDR', 'Dopamine', ['DOP#2']).
neuron(87, 'CEPVL', 'Dopamine', ['DOP#2']).
neuron(88, 'CEPVR', 'Dopamine', ['DOP#2']).
neuron(89, 'DA1', 'Acetylcholine', ['UNC#8']).
neuron(90, 'DA2', 'Acetylcholine', ['UNC#8']).
neuron(91, 'DA3', 'Acetylcholine', ['UNC#8']).
neuron(92, 'DA4', 'Acetylcholine', ['UNC#8']).
neuron(93, 'DA5', 'Acetylcholine', ['UNC#8']).
neuron(94, 'DA6', 'Acetylcholine', ['UNC#8']).
neuron(95, 'DA7', 'Acetylcholine', ['UNC#8']).
neuron(96, 'DA8', 'Acetylcholine', ['UNC#8']).
neuron(97, 'DA9', 'Acetylcholine', ['SER#2']).
neuron(98, 'DB1', 'Acetylcholine', ['null']).
neuron(99, 'DB2', 'Acetylcholine', ['null']).
neuron(100, 'DB3', 'Acetylcholine', ['null']).
neuron(101, 'DB4', 'Acetylcholine', ['null']).
neuron(102, 'DB5', 'Acetylcholine', ['null']).
neuron(103, 'DB6', 'Acetylcholine', ['null']).
neuron(104, 'DB7', 'Acetylcholine', ['null']).
neuron(105, 'DD1', 'GABA', ['NPR#1', 'GGR#2', 'UNC#8']).
neuron(106, 'DD2', 'GABA', ['NPR#1', 'GGR#2', 'UNC#8']).
neuron(107, 'DD3', 'GABA', ['NPR#1', 'GGR#2', 'UNC#8']).
neuron(108, 'DD4', 'GABA', ['NPR#1', 'GGR#2', 'UNC#8']).
neuron(109, 'DD5', 'GABA', ['NPR#1', 'GGR#2', 'UNC#8']).
neuron(110, 'DD6', 'GABA', ['NPR#1', 'GGR#2', 'UNC#8']).
neuron(111, 'DVA', 'GABA', ['GLR#4', 'GLR#5', 'NMR#1', 'SER#2', 'SER#4', 'GGR#3', 'GGR#2']).
neuron(112, 'DVB', 'GABA', ['null']).
neuron(113, 'DVC', 'GABA', ['GLR#1', 'SER#4']).
neuron(114, 'FLPL', 'Glutamate', ['OSM#9', 'DEG#3', 'DES#2', 'GLR#4', 'MEC#10', 'DEL#1', 'UNC#8']).
neuron(115, 'FLPR', 'Glutamate', ['OSM#9', 'DEG#3', 'DES#2', 'GLR#4', 'MEC#10', 'DEL#1', 'UNC#8']).
neuron(116, 'HSNL', 'Serotonin', ['MEC#6', 'GAR#2', 'GLR#5', 'GGR#2']).
neuron(116, 'HSNL', 'Acetylcholine', ['MEC#6', 'GAR#2', 'GLR#5', 'GGR#2']).
neuron(117, 'HSNR', 'Acetylcholine', ['MEC#6', 'GAR#2', 'GLR#5', 'GGR#2']).
neuron(117, 'HSNR', 'Serotonin', ['MEC#6', 'GAR#2', 'GLR#5', 'GGR#2']).
neuron(118, 'I1L', 'Acetylcholine', ['GLR#7', 'GLR#8', 'ACM#2']).
neuron(119, 'I1R', 'Acetylcholine', ['GLR#7', 'GLR#8', 'ACM#2']).
neuron(120, 'I2L', 'Glutamate', ['GLR#7', 'GLR#8', 'ACM#2', 'SER#7b']).
neuron(121, 'I2R', 'Glutamate', ['GLR#7', 'GLR#8', 'ACM#2', 'SER#7b']).
neuron(122, 'I3', 'Glutamate', ['GLR#7', 'GLR7b', 'AEX#2']).
neuron(123, 'I4', 'Glutamate', ['null']).
neuron(124, 'I5', 'Serotonin', ['null']).
neuron(124, 'I5', 'Glutamate', ['null']).
neuron(125, 'I6', 'Acetylcholine', ['GLR#7', 'GLR#b8', 'SER#7b']).
neuron(126, 'IL1DL', 'Glutamate', ['DEG#3', 'MEC#6']).
neuron(127, 'IL1DR', 'Glutamate', ['DEG#3', 'MEC#6']).
neuron(128, 'IL1L', 'Glutamate', ['DEG#3', 'MEC#6']).
neuron(129, 'IL1R', 'Glutamate', ['DEG#3', 'MEC#6']).
neuron(130, 'IL1VL', 'Glutamate', ['DEG#3', 'MEC#6']).
neuron(131, 'IL1VR', 'Glutamate', ['DEG#3', 'MEC#6']).
neuron(132, 'IL2DL', 'Serotonin', ['DES#2']).
neuron(133, 'IL2DR', 'Serotonin', ['DES#2']).
neuron(134, 'IL2L', 'Acetylcholine', ['NPR#1']).
neuron(135, 'IL2R', 'Acetylcholine', ['NPR#1']).
neuron(136, 'IL2VL', 'Serotonin', ['DES#2']).
neuron(137, 'IL2VR', 'Serotonin', ['DES#2']).
neuron(138, 'LUAL', 'Glutamate', ['GLR#5', 'SER#2']).
neuron(139, 'LUAR', 'Glutamate', ['GLR#5', 'SER#2']).
neuron(140, 'M1', 'Acetylcholine', ['GLR#2', 'AVR#14']).
neuron(141, 'M2L', 'Acetylcholine', ['SER#7b']).
neuron(142, 'M2R', 'Acetylcholine', ['SER#7b']).
neuron(143, 'M3L', 'Glutamate', ['GLR#8', 'NPR#1']).
neuron(144, 'M3R', 'Glutamate', ['GLR#8', 'NPR#1']).
neuron(145, 'M4', 'Acetylcholine', ['SER7b', 'ACM#2', 'GLR#8']).
neuron(146, 'M5', 'Acetylcholine', ['GLR#8']).
neuron(147, 'MCL', 'Acetylcholine', ['GLR#8', 'SER#7']).
neuron(148, 'MCR', 'Acetylcholine', ['GLR#8', 'SER#7']).
neuron(149, 'MI', 'null', ['GLR#2 ']).
neuron(150, 'NSML', 'Serotonin', ['GLR#7', 'GLR#8', 'SER#2', 'AEX#2']).
neuron(150, 'NSML', 'Glutamate', ['GLR#7', 'GLR#8', 'SER#2', 'AEX#2']).
neuron(151, 'NSMR', 'Serotonin', ['GLR#7', 'GLR#8', 'SER#2', 'AEX#2']).
neuron(151, 'NSMR', 'Glutamate', ['GLR#7', 'GLR#8', 'SER#2', 'AEX#2']).
neuron(152, 'OLLL', 'Glutamate', ['SER#2']).
neuron(153, 'OLLR', 'Glutamate', ['SER#2']).
neuron(154, 'OLQDL', 'Glutamate', ['OSM#9', 'OCR#4', 'NPR#1']).
neuron(155, 'OLQDR', 'Glutamate', ['OSM#9', 'OCR#4', 'NPR#1']).
neuron(156, 'OLQVL', 'Glutamate', ['OSM#9', 'OCR#4', 'NPR#1']).
neuron(157, 'OLQVR', 'Glutamate', ['OSM#9', 'OCR#4', 'NPR#1']).
neuron(158, 'PDA', 'Serotonin', ['EXP#1', 'UNC#8', 'SER#2']).
neuron(159, 'PDB', 'FMRFamide', ['UNC#8']).
neuron(160, 'PDEL', 'Dopamine', ['DOP#2']).
neuron(161, 'PDER', 'Dopamine', ['DOP#2']).
neuron(162, 'PHAL', 'Glutamate', ['GCY#12', 'OSM#9', 'OCR#2', 'SRG#13', 'SRB#6', 'NPR#1']).
neuron(163, 'PHAR', 'Glutamate', ['GCY#12', 'OSM#9', 'OCR#2', 'SRG#13', 'SRB#6', 'NPR#1']).
neuron(164, 'PHBL', 'Serotonin', ['OSM#9', 'OCR#2', 'SRB#6', 'NPR#1']).
neuron(165, 'PHBR', 'Serotonin', ['OSM#9', 'OCR#2', 'SRB#6', 'NPR#1']).
neuron(166, 'PHCL', 'Glutamate', ['DOP#1']).
neuron(167, 'PHCR', 'Glutamate', ['DOP#1']).
neuron(168, 'PLML', 'Glutamate', ['MEC#2', 'MEC#4', 'MEC#6', 'MEC#9DES#2', 'DOP#1']).
neuron(169, 'PLMR', 'Glutamate', ['MEC#2', 'MEC#4', 'MEC#6', 'MEC#9', 'DES#2', 'DOP#1']).
neuron(170, 'PLNL', 'Acetylcholine', ['DOP#1', 'GCY#35']).
neuron(171, 'PLNR', 'Acetylcholine', ['DOP#1', 'GCY#35']).
neuron(172, 'PQR', 'Glutamate', ['GCY#32', 'NPR#1', 'GCY#35 ']).
neuron(173, 'PVCL', 'Glutamate', ['DEG#3', 'SER#2']).
neuron(174, 'PVCR', 'Glutamate', ['DEG#3', 'SER#2']).
neuron(175, 'PVDL', 'Glutamate', ['MEC#10', 'MEC#9', 'MEC#6', 'OSM#9', 'SER#2', 'DEG#3', 'DOP#3']).
neuron(176, 'PVDR', 'Glutamate', ['MEC#10', 'MEC#9', 'MEC#6', 'OSM#9', 'SER#2', 'DEG#3', 'DOP#3']).
neuron(177, 'PVM', 'Glutamate', ['GAR#1', 'MEC#2', 'MEC#4', 'MEC#10', 'MEC#9']).
neuron(178, 'PVNL', 'Glutamate', ['null']).
neuron(179, 'PVNR', 'Glutamate', ['null']).
neuron(180, 'PVPL', 'Glutamate', ['null']).
neuron(181, 'PVPR', 'Glutamate', ['null']).
neuron(182, 'PVQL', 'null', ['GLR#1', 'GLR#5', 'SRA#6', 'DOP#1', 'GGR#1']).
neuron(183, 'PVQR', 'null', ['GLR#1', 'GLR#5', 'SRA#6', 'DOP#1', 'GGR#1']).
neuron(184, 'PVR', 'Glutamate', ['GGR#1']).
neuron(185, 'PVT', 'Glutamate', ['SER#2', 'SER#4']).
neuron(186, 'PVWL', 'Serotonin', ['null']).
neuron(187, 'PVWR', 'Serotonin', ['null']).
neuron(188, 'RIAL', 'GABA', ['Glr#3', 'GLR#6', 'SER#2']).
neuron(189, 'RIAR', 'GABA', ['Glr#3', 'GLR#6', 'SER#2']).
neuron(190, 'RIBL', 'Glutamate', ['DOP#1']).
neuron(191, 'RIBR', 'Glutamate', ['DOP#1']).
neuron(192, 'RICL', 'Octapamine', ['DOP#3', 'SER#2']).
neuron(193, 'RICR', 'Octapamine', ['DOP#3', 'SER#2']).
neuron(194, 'RID', 'GABA', ['EXP#1', 'SER#2']).
neuron(195, 'RIFL', 'Glutamate', ['null']).
neuron(196, 'RIFR', 'Glutamate', ['null']).
neuron(197, 'RIGL', 'FRMFemide', ['null']).
neuron(198, 'RIGR', 'FRMFemide', ['null']).
neuron(199, 'RIH', 'Serotonin', ['null']).
neuron(200, 'RIML', 'Tyramine', ['DOP#1']).
neuron(200, 'RIML', 'Acetylcholine', ['DOP#1']).
neuron(201, 'RIMR', 'Tyramine', ['DOP#1']).
neuron(201, 'RIMR', 'Acetylcholine', ['DOP#1']).
neuron(202, 'RIPL', 'Serotonin', ['null']).
neuron(203, 'RIPR', 'Serotonin', ['null']).
neuron(204, 'RIR', 'null', ['null']).
neuron(205, 'RIS', 'GABA', ['GLR#1', 'SER#4', 'DOP#1']).
neuron(206, 'RIVL', 'GABA', ['null']).
neuron(207, 'RIVR', 'GABA', ['null']).
neuron(208, 'RMDDL', 'Acetylcholine', ['null']).
neuron(209, 'RMDDR', 'Acetylcholine', ['null']).
neuron(210, 'RMDL', 'Acetylcholine', ['null']).
neuron(211, 'RMDR', 'Acetylcholine', ['null']).
neuron(212, 'RMDVL', 'Acetylcholine', ['null']).
neuron(213, 'RMDVR', 'Acetylcholine', ['null']).
neuron(214, 'RMED', 'GABA', ['AVR#15', 'SER#2']).
neuron(215, 'RMEL', 'GABA', ['GLR#1', 'SER#2']).
neuron(216, 'RMER', 'GABA', ['GLR#1', 'SER#2']).
neuron(217, 'RMEV', 'GABA', ['AVR#15', 'SER#2']).
neuron(218, 'RMFL', 'Glutamate', ['null']).
neuron(219, 'RMFR', 'Glutamate', ['null']).
neuron(220, 'RMGL', 'FRMFemide', ['null']).
neuron(221, 'RMGR', 'FRMFemide', ['null']).
neuron(222, 'RMHL', 'Glutamate', ['null']).
neuron(223, 'RMHR', 'Glutamate', ['null']).
neuron(224, 'SAADL', 'Acetylcholine', ['null']).
neuron(225, 'SAADR', 'Acetylcholine', ['null']).
neuron(226, 'SAAVL', 'Acetylcholine', ['null']).
neuron(227, 'SAAVR', 'Acetylcholine', ['null']).
neuron(228, 'SABD', 'Acetylcholine', ['EXP#1', 'SER#2']).
neuron(229, 'SABVL', 'Acetylcholine', ['DEL#1', 'SER#2']).
neuron(230, 'SABVR', 'Acetylcholine', ['DEL#1', 'SER#2']).
neuron(231, 'SDQL', 'Acetylcholine', ['GCY#35', 'SER#2']).
neuron(232, 'SDQR', 'Acetylcholine', ['GCY#35', 'SER#2']).
neuron(233, 'SIADL', 'Acetylcholine', ['DOP#3', 'GGR#3', 'GGR#2', 'SER#2']).
neuron(234, 'SIADR', 'Acetylcholine', ['DOP#3', 'GGR#3', 'GGR#2', 'SER#2']).
neuron(235, 'SIAVL', 'Acetylcholine', ['GGR#2', 'DOP#3', 'SER#2']).
neuron(236, 'SIAVR', 'Acetylcholine', ['GGR#2', 'DOP#3', 'SER#2']).
neuron(237, 'SIBDL', 'Acetylcholine', ['null']).
neuron(238, 'SIBDR', 'Acetylcholine', ['null']).
neuron(239, 'SIBVL', 'Acetylcholine', ['null']).
neuron(240, 'SIBVR', 'Acetylcholine', ['null']).
neuron(241, 'SMBDL', 'Acetylcholine', ['null']).
neuron(242, 'SMBDR', 'Acetylcholine', ['null']).
neuron(243, 'SMBVL', 'Acetylcholine', ['null']).
neuron(244, 'SMBVR', 'Acetylcholine', ['null']).
neuron(245, 'SMDDL', 'Acetylcholine', ['GGR#2', 'GGR#3']).
neuron(246, 'SMDDR', 'Acetylcholine', ['GGR#2', 'GGR#3']).
neuron(247, 'SMDVL', 'Acetylcholine', ['GGR#1', 'GGR#2']).
neuron(248, 'SMDVR', 'Acetylcholine', ['GGR#1', 'GGR#2']).
neuron(249, 'URADL', 'Acetylcholine', ['null']).
neuron(250, 'URADR', 'Acetylcholine', ['null']).
neuron(251, 'URAVL', 'Acetylcholine', ['null']).
neuron(252, 'URAVR', 'Acetylcholine', ['null']).
neuron(253, 'URBL', 'Acetylcholine', ['null']).
neuron(254, 'URBR', 'Acetylcholine', ['null']).
neuron(255, 'URXL', 'Glutamate', ['GCY#32', 'GCY#35', 'NPR#1', 'SRA#10']).
neuron(256, 'URXR', 'Glutamate', ['GCY#32', 'GCY#35', 'NPR#1', 'SRA#10']).
neuron(257, 'URYDL', 'Glutamate', ['null']).
neuron(258, 'URYDR', 'Glutamate', ['null']).
neuron(259, 'URYVL', 'Glutamate', ['null']).
neuron(260, 'URYVR', 'Glutamate', ['null']).
neuron(261, 'VA1', 'Acetylcholine', ['DEL#1']).
neuron(262, 'VA10', 'Acetylcholine', ['DEL#1']).
neuron(263, 'VA11', 'Acetylcholine', ['DEL#1']).
neuron(264, 'VA12', 'Acetylcholine', ['DEL#1']).
neuron(265, 'VA2', 'Acetylcholine', ['DEL#1']).
neuron(266, 'VA3', 'Acetylcholine', ['DEL#1']).
neuron(267, 'VA4', 'Acetylcholine', ['DEL#1']).
neuron(268, 'VA5', 'Acetylcholine', ['DEL#1']).
neuron(269, 'VA6', 'Acetylcholine', ['DEL#1']).
neuron(270, 'VA7', 'Acetylcholine', ['DEL#1']).
neuron(271, 'VA8', 'Acetylcholine', ['DEL#1']).
neuron(272, 'VA9', 'Acetylcholine', ['DEL#1']).
neuron(273, 'VB1', 'Acetylcholine', ['DEL#1']).
neuron(274, 'VB10', 'Acetylcholine', ['DEL#1']).
neuron(275, 'VB11', 'Acetylcholine', ['DEL#1']).
neuron(276, 'VB2', 'Acetylcholine', ['DEL#1']).
neuron(277, 'VB3', 'Acetylcholine', ['DEL#1']).
neuron(278, 'VB4', 'Acetylcholine', ['DEL#1']).
neuron(279, 'VB5', 'Acetylcholine', ['DEL#1']).
neuron(280, 'VB6', 'Acetylcholine', ['DEL#1']).
neuron(281, 'VB7', 'Acetylcholine', ['DEL#1']).
neuron(282, 'VB8', 'Acetylcholine', ['DEL#1']).
neuron(283, 'VB9', 'Acetylcholine', ['DEL#1']).
neuron(284, 'VC1', 'Acetylcholine', ['GLR#5']).
neuron(284, 'VC1', 'Serotonin', ['GLR#5']).
neuron(285, 'VC2', 'Acetylcholine', ['GLR#5']).
neuron(285, 'VC2', 'Serotonin', ['GLR#5']).
neuron(286, 'VC3', 'Acetylcholine', ['GLR#5']).
neuron(286, 'VC3', 'Serotonin', ['GLR#5']).
neuron(287, 'VC4', 'Acetylcholine', ['GLR#5']).
neuron(287, 'VC4', 'Serotonin', ['GLR#5']).
neuron(288, 'VC5', 'Acetylcholine', ['GLR#5']).
neuron(288, 'VC5', 'Serotonin', ['GLR#5']).
neuron(289, 'VC6', 'Acetylcholine', ['GLR#5']).
neuron(289, 'VC6', 'Serotonin', ['GLR#5']).
neuron(290, 'VD1', 'GABA', ['NPR#1']).
neuron(291, 'VD10', 'GABA', ['NPR#1']).
neuron(292, 'VD11', 'GABA', ['NPR#1']).
neuron(293, 'VD12', 'GABA', ['NPR#1']).
neuron(294, 'VD13', 'GABA', ['NPR#1']).
neuron(295, 'VD2', 'GABA', ['NPR#1']).
neuron(296, 'VD3', 'GABA', ['NPR#1']).
neuron(297, 'VD4', 'GABA', ['NPR#1']).
neuron(298, 'VD5', 'GABA', ['NPR#1']).
neuron(299, 'VD6', 'GABA', ['NPR#1']).
neuron(300, 'VD7', 'GABA', ['NPR#1']).
neuron(301, 'VD8', 'GABA', ['NPR#1']).
neuron(302, 'VD9', 'GABA', ['NPR#1']).*/

# Basic information about each neurotransmitter and what receptor receives it
transmit_recept('Acetylcholine', 'ACM#2', 'inhibitory').
transmit_recept('Acetylcholine', 'DEG#3 ', 'excitatory').
transmit_recept('Acetylcholine', 'DES#2', 'excitatory').
transmit_recept('Acetylcholine', 'GAR#1', 'inhibitory').
transmit_recept('Acetylcholine', 'GAR#2', 'inhibitory').
transmit_recept('Capsaicin', 'OCR#1 ', 'excitatory').
transmit_recept('Capsaicin', 'OCR#2', 'excitatory').
transmit_recept('Capsaicin', 'OSM#9', 'excitatory').
transmit_recept('Dopamine', 'DOP#1', 'inhibitory').
transmit_recept('Dopamine', 'DOP#2', 'inhibitory').
transmit_recept('Dopamine', 'DOP#3', 'inhibitory').
transmit_recept('FMRFamide', 'NPR#1 ', 'inhibitory').
transmit_recept('GABA', 'EXP#1', 'excitatory').
transmit_recept('GABA', 'GGR#1', 'inhibitory').
transmit_recept('GABA', 'GGR#2', 'inhibitory').
transmit_recept('GABA', 'GGR#3 ', 'inhibitory').
transmit_recept('Glutamate', 'AVR#14', 'inhibitory').
transmit_recept('Glutamate', 'AVR#15', 'inhibitory').
transmit_recept('Glutamate', 'GLR#1', 'excitatory').
transmit_recept('Glutamate', 'GLR#2', 'excitatory').
transmit_recept('Glutamate', 'GLR#3', 'excitatory').
transmit_recept('Glutamate', 'GLR#4', 'excitatory').
transmit_recept('Glutamate', 'GLR#5', 'excitatory').
transmit_recept('Glutamate', 'GLR#6', 'excitatory').
transmit_recept('Glutamate', 'GLR#7', 'excitatory').
transmit_recept('Glutamate', 'GLR#8', 'excitatory').
transmit_recept('Glutamate', 'NMR#1', 'excitatory').
transmit_recept('Glutamate', 'NMR#2', 'excitatory').
transmit_recept('Membrane', 'DAF#11', 'inhibitory').
transmit_recept('Membrane', 'DEL#1', 'excitatory ').
transmit_recept('Membrane', 'GCY#12', 'excitatory').
transmit_recept('Membrane', 'GCY#32', 'excitatory').
transmit_recept('Membrane', 'GCY#33', 'excitatory').
transmit_recept('Membrane', 'GCY#35 ', 'excitatory').
transmit_recept('Membrane', 'GCY#5', 'excitatory').
transmit_recept('Membrane', 'GCY#6', 'excitatory').
transmit_recept('Membrane', 'GCY#7', 'excitatory').
transmit_recept('Membrane', 'MEC#10 ', 'excitatory').
transmit_recept('Membrane', 'MEC#2', 'excitatory').
transmit_recept('Membrane', 'MEC#4 ', 'excitatory').
transmit_recept('Membrane', 'MEC#6', 'excitatory').
transmit_recept('Membrane', 'MEC#9 ', 'Unknown').
transmit_recept('Membrane', 'SRA#10', 'Unknown').
transmit_recept('Membrane', 'UNC#8', 'exitatory').
transmit_recept('Serotonin', 'SER#2 ', 'Unknown').
transmit_recept('Serotonin', 'SER#4 ', 'inhibitory').
transmit_recept('Serotonin', 'SER7b ', 'excitatory').
transmit_recept('Unknown', 'AEX#2', 'inhibitory').
transmit_recept('Unknown', 'ODR#10', 'Unknown').
transmit_recept('Unknown', 'SRA#11', 'Unknown').
transmit_recept('Unknown', 'SRA#6', 'Unknown').
transmit_recept('Unknown', 'SRA#7', 'Unknown').
transmit_recept('Unknown', 'SRA#9', 'Unknown').
transmit_recept('Unknown', 'SRB#6', 'Unknown').
transmit_recept('Unknown', 'SRD#1', 'Unknown').
transmit_recept('Unknown', 'SRE#1', 'Unknown').
transmit_recept('Unknown', 'SRG#13 ', 'Unknown').
transmit_recept('Unknown', 'SRG#2', 'Unknown').
transmit_recept('Unknown', 'SRG#8', 'Unknown').
transmit_recept('Unknown', 'STR#1', 'Unknown').
transmit_recept('Unknown', 'STR#2', 'Unknown').
transmit_recept('Unknown', 'STR#3', 'Unknown').

#Information from each Neuron -- need to verify if we can find the original
# sources for this information

neuron(1, 'ADAL', 'Glutamate', ['null']).
neuron(2, 'ADAR', 'Glutamate', ['null']).
neuron(3, 'ADEL', 'Dopamine', ['DOP#2', 'EXP#1']).
neuron(4, 'ADER', 'Dopamine', ['DOP#2', 'EXP#1']).
neuron(5, 'ADFL', 'Serotonin', ['OSM#9', 'OCR#2', 'SRB#6']).
neuron(6, 'ADFR', 'Serotonin', ['OSM#9 ', 'OCR#2', 'SRB#6']).
neuron(7, 'ADLL', 'null', ['OSM#9', 'OCR#1', 'OCR#2', 'SRE#1', 'SRB#6']).
neuron(8, 'ADLR', 'null', ['OSM#9', 'OCR#1', 'OCR#2', 'SRE#1', 'SRB#6']).
neuron(9, 'AFDL', 'null', ['GCY#12']).
neuron(10, 'AFDR', 'null', ['GCY#12']).
neuron(11, 'AIAL', 'Acetylcholine', ['GLR#2', 'SRA#11']).
neuron(12, 'AIAR', 'Acetylcholine', ['GLR#2', 'SRA#11']).
neuron(13, 'AIBL', 'null', ['GLR#1', 'GLR#2', 'GLR#5', 'GGR#1']).
neuron(14, 'AIBR', 'null', ['GLR#1', 'GLR#2', 'GLR#5', 'GGR#1']).
neuron(15, 'AIML', 'Serotonin', ['null']).
neuron(16, 'AIMR', 'Serotonin', ['null']).
neuron(17, 'AINL', 'Glutamate', ['null']).
neuron(18, 'AINR', 'Glutamate', ['null']).
neuron(19, 'AIYL', 'Acetylcholine', ['SER#2', 'SRA#11']).
neuron(20, 'AIYR', 'Acetylcholine', ['SER#2', 'SRA#11']).
neuron(21, 'AIZL', 'null', ['SER#2']).
neuron(22, 'AIZR', 'null', ['SER#2']).
neuron(23, 'ALA', 'null', ['SRA#10']).
neuron(24, 'ALML', 'Glutamate', ['MEC#2', 'MEC#4', 'MEC#10', 'MEC#9', 'MEC#6', 'DEG#3', 'DES#2', 'GLR#8', 'DOP#1']).
neuron(25, 'ALMR', 'Glutamate', ['MEC#2', 'MEC#4', 'MEC#10', 'MEC#9', 'MEC#6', 'DEG#3', 'DES#2', 'GLR#8', 'DOP#1']).
neuron(26, 'ALNL', 'Acetylcholine', ['SER#2', 'DOP#1', 'GCY#35']).
neuron(27, 'ALNR', 'Acetylcholine', ['SER#2', 'DOP#1', 'GCY#35']).
neuron(28, 'AQR', 'null', ['GCY#32', 'NPR#1', 'GCY#35']).
neuron(29, 'AS1', 'Acetylcholine', ['null']).
neuron(30, 'AS10', 'Acetylcholine', ['null']).
neuron(31, 'AS11', 'Acetylcholine', ['null']).
neuron(32, 'AS2', 'Acetylcholine', ['null']).
neuron(33, 'AS3', 'Acetylcholine', ['null']).
neuron(34, 'AS4', 'Acetylcholine', ['null']).
neuron(35, 'AS5', 'Acetylcholine', ['null']).
neuron(36, 'AS6', 'Acetylcholine', ['null']).
neuron(37, 'AS7', 'Acetylcholine', ['null']).
neuron(38, 'AS8', 'Acetylcholine', ['null']).
neuron(39, 'AS9', 'Acetylcholine', ['null']).
neuron(40, 'ASEL', 'null', ['GCY#6', 'GCY#7', 'OSM#9', 'GCY#12', 'DOP#3']).
neuron(41, 'ASER', 'null', ['GCY#5', 'OSM#9', 'GCY#12', 'DOP#3']).
neuron(42, 'ASGL', 'null', ['OSM#9', 'NPR#1']).
neuron(43, 'ASGR', 'null', ['NPR#1', 'OSM#9']).
neuron(44, 'ASHL', 'Glutamate', ['OSM#9', 'OCR#2', 'SRA#6', 'SRB#6', 'NPR#1', 'UNC#8']).
neuron(45, 'ASHR', 'Glutamate', ['OSM#9', 'OCR#2', 'SRA#6', 'SRB#6', 'NPR#1', 'UNC#8']).
neuron(46, 'ASIL', 'null', ['SRD#1', 'STR#2', 'STR#3', 'DAF#11', 'SRA#6']).
neuron(47, 'ASIR', 'null', ['SRD#1', 'STR#2', 'STR#3', 'DAF#11', 'SRA#6']).
neuron(48, 'ASJL', 'null', ['OSM#9', 'SRE#1', 'DAF#11']).
neuron(49, 'ASJR', 'null', ['OSM#9', 'SRE#1', 'DAF#11']).
neuron(50, 'ASKL', 'Glutamate', ['OSM#9', 'SRA#7', 'SRA#9', 'SRG#2', 'SRG#8', 'DAF#11']).
neuron(51, 'ASKR', 'Glutamate', ['OSM#9', 'SRA#7', 'SRA#9', 'SRG#2', 'SRG#8', 'DAF#11']).
neuron(52, 'AUAL', 'Glutamate', ['GLR#4', 'NPR#1', 'SER#2', 'DOP#1', 'SER#2']).
neuron(53, 'AUAR', 'Glutamate', ['GLR#4', 'NPR#1', 'SER#2', 'DOP#1', 'SER#2']).
neuron(54, 'AVAL', 'FMRFamide', ['GLR#1', 'GLR#2', 'GLR#4', 'GLR#5', 'NMR#1', 'GGR#3', 'GGR#2']).
neuron(55, 'AVAR', 'FMRFamide', ['GLR#1', 'GLR#2', 'GLR#4', 'GLR#5', 'NMR#1', 'GGR#3', 'GGR#2']).
neuron(56, 'AVBL', 'null', ['GLR#1', 'GLR#5', 'SRA#11', 'GGR#3', 'UNC#8', 'GGR#3']).
neuron(57, 'AVBR', 'null', ['GLR#1', 'GLR#5', 'SRA#11', 'GGR#3', 'UNC#8', 'GGR#3']).
neuron(58, 'AVDL', 'Glutamate', ['GLR#1', 'GLR#2', 'GLR#5', 'NMR#1', 'NMR#2', 'UNC#8']).
neuron(59, 'AVDR', 'Glutamate', ['GLR#1', 'GLR#2', 'GLR#5', 'NMR#1', 'NMR#2', 'UNC#8']).
neuron(60, 'AVEL', 'FMRFamide', ['GLR#1', 'GLR#2', 'GLR#5', 'NMR#1', 'NMR#2']).
neuron(61, 'AVER', 'FMRFamide', ['GLR#1', 'GLR#2', 'GLR#5', 'NMR#1', 'NMR#2']).
neuron(62, 'AVFL', 'null', ['null']).
neuron(63, 'AVFR', 'null', ['null']).
neuron(64, 'AVG', 'null', ['GLR#1', 'GLR#2', 'NMR#1', 'NMR#2', 'DEG#3']).
neuron(65, 'AVHL', 'null', ['GLR#4', 'SER#2', 'GGR#1']).
neuron(66, 'AVHR', 'null', ['GLR#4', 'SER#2', 'GGR#1']).
neuron(67, 'AVJL', 'Glutamate', ['GLR#1']).
neuron(68, 'AVJR', 'Glutamate', ['GLR#1']).
neuron(69, 'AVKL', 'FMRFamide', ['GLR#5']).
neuron(70, 'AVKR', 'FMRFamide', ['GLR#5']).
neuron(71, 'AVL', 'GABA', ['null']).
neuron(72, 'AVM', 'Glutamate', ['MEC#2', 'MEC#4', 'MEC#10', 'MEC#9', 'MEC#6', 'DOP#1', 'GCY#35']).
neuron(73, 'AWAL', 'null', ['ODR#10', 'OSM#9', 'OCR#1', 'OCR#2']).
neuron(74, 'AWAR', 'null', ['ODR#10', 'OSM#9', 'OCR#1', 'OCR#2']).
neuron(75, 'AWBL', 'null', ['STR#1', 'DAF#11', 'AEX#2']).
neuron(76, 'AWBR', 'null', ['STR#1', 'DAF#11', 'AEX#2']).
neuron(77, 'AWCL', 'null', ['OSM#9', 'DAF#11', 'STR#2', 'GCY#12']).
neuron(78, 'AWCR', 'null', ['OSM#9', 'DAF#11', 'STR#2', 'GCY#12']).
neuron(79, 'BAGL', 'null', ['GCY#33']).
neuron(80, 'BAGR', 'null', ['GCY#33']).
neuron(81, 'BDUL', 'null', ['GLR#8']).
neuron(82, 'BDUR', 'null', ['GLR#8', 'SER#2', 'GCY#35']).
neuron(83, 'CANL*', 'Monoamine', ['SER#2', 'GGR#2']).
neuron(84, 'CANR*', 'Monoamine', ['SER#2', 'GGR#2']).
neuron(85, 'CEPDL', 'Dopamine', ['DOP#2']).
neuron(86, 'CEPDR', 'Dopamine', ['DOP#2']).
neuron(87, 'CEPVL', 'Dopamine', ['DOP#2']).
neuron(88, 'CEPVR', 'Dopamine', ['DOP#2']).
neuron(89, 'DA1', 'Acetylcholine', ['UNC#8']).
neuron(90, 'DA2', 'Acetylcholine', ['UNC#8']).
neuron(91, 'DA3', 'Acetylcholine', ['UNC#8']).
neuron(92, 'DA4', 'Acetylcholine', ['UNC#8']).
neuron(93, 'DA5', 'Acetylcholine', ['UNC#8']).
neuron(94, 'DA6', 'Acetylcholine', ['UNC#8']).
neuron(95, 'DA7', 'Acetylcholine', ['UNC#8']).
neuron(96, 'DA8', 'Acetylcholine', ['UNC#8']).
neuron(97, 'DA9', 'Acetylcholine', ['SER#2']).
neuron(98, 'DB1', 'Acetylcholine', ['null']).
neuron(99, 'DB2', 'Acetylcholine', ['null']).
neuron(100, 'DB3', 'Acetylcholine', ['null']).
neuron(101, 'DB4', 'Acetylcholine', ['null']).
neuron(102, 'DB5', 'Acetylcholine', ['null']).
neuron(103, 'DB6', 'Acetylcholine', ['null']).
neuron(104, 'DB7', 'Acetylcholine', ['null']).
neuron(105, 'DD1', 'GABA', ['NPR#1', 'GGR#2', 'UNC#8']).
neuron(106, 'DD2', 'GABA', ['NPR#1', 'GGR#2', 'UNC#8']).
neuron(107, 'DD3', 'GABA', ['NPR#1', 'GGR#2', 'UNC#8']).
neuron(108, 'DD4', 'GABA', ['NPR#1', 'GGR#2', 'UNC#8']).
neuron(109, 'DD5', 'GABA', ['NPR#1', 'GGR#2', 'UNC#8']).
neuron(110, 'DD6', 'GABA', ['NPR#1', 'GGR#2', 'UNC#8']).
neuron(111, 'DVA', 'null', ['GLR#4', 'GLR#5', 'NMR#1', 'SER#2', 'SER#4', 'GGR#3', 'GGR#2']).
neuron(112, 'DVB', 'GABA', ['null']).
neuron(113, 'DVC', 'null', ['GLR#1', 'SER#4']).
neuron(114, 'FLPL', 'Glutamate', ['OSM#9', 'DEG#3', 'DES#2', 'GLR#4', 'MEC#10', 'DEL#1', 'UNC#8']).
neuron(115, 'FLPR', 'Glutamate', ['OSM#9', 'DEG#3', 'DES#2', 'GLR#4', 'MEC#10', 'DEL#1', 'UNC#8']).
neuron(116, 'HSNL', 'Serotonin', ['MEC#6', 'GAR#2', 'GLR#5', 'GGR#2']).
neuron(116, 'HSNL', 'Acetylcholine', ['MEC#6', 'GAR#2', 'GLR#5', 'GGR#2']).
neuron(117, 'HSNR', 'Acetylcholine', ['MEC#6', 'GAR#2', 'GLR#5', 'GGR#2']).
neuron(117, 'HSNR', 'Serotonin', ['MEC#6', 'GAR#2', 'GLR#5', 'GGR#2']).
neuron(118, 'I1L', 'Acetylcholine', ['GLR#7', 'GLR#8', 'ACM#2']).
neuron(119, 'I1R', 'Acetylcholine', ['GLR#7', 'GLR#8', 'ACM#2']).
neuron(120, 'I2L', 'null', ['GLR#7', 'GLR#8', 'ACM#2', 'SER#7b']).
neuron(121, 'I2R', 'null', ['GLR#7', 'GLR#8', 'ACM#2', 'SER#7b']).
neuron(122, 'I3', 'null', ['GLR#7', 'GLR7b', 'AEX#2']).
neuron(123, 'I4', 'null', ['null']).
neuron(124, 'I5', 'Serotonin', ['null']).
%neuron(124, 'I5', 'Glutamate', ['null']).
neuron(125, 'I6', 'Acetylcholine', ['GLR#7', 'GLR#b8', 'SER#7b']).
neuron(126, 'IL1DL', 'Glutamate', ['DEG#3', 'MEC#6']).
neuron(127, 'IL1DR', 'Glutamate', ['DEG#3', 'MEC#6']).
neuron(128, 'IL1L', 'Glutamate', ['DEG#3', 'MEC#6']).
neuron(129, 'IL1R', 'Glutamate', ['DEG#3', 'MEC#6']).
neuron(130, 'IL1VL', 'Glutamate', ['DEG#3', 'MEC#6']).
neuron(131, 'IL1VR', 'Glutamate', ['DEG#3', 'MEC#6']).
neuron(132, 'IL2DL', 'null', ['DES#2']).
neuron(133, 'IL2DR', 'null', ['DES#2']).
neuron(134, 'IL2L', 'Acetylcholine', ['NPR#1']).
neuron(135, 'IL2R', 'Acetylcholine', ['NPR#1']).
neuron(136, 'IL2VL', 'null', ['DES#2']).
neuron(137, 'IL2VR', 'null', ['DES#2']).
neuron(138, 'LUAL', 'Glutamate', ['GLR#5', 'SER#2']).
neuron(139, 'LUAR', 'Glutamate', ['GLR#5', 'SER#2']).
neuron(140, 'M1', 'Acetylcholine', ['GLR#2', 'AVR#14']).
neuron(141, 'M2L', 'Acetylcholine', ['SER#7b']).
neuron(142, 'M2R', 'Acetylcholine', ['SER#7b']).
neuron(143, 'M3L', 'Glutamate', ['GLR#8', 'NPR#1']).
neuron(144, 'M3R', 'Glutamate', ['GLR#8', 'NPR#1']).
neuron(145, 'M4', 'Acetylcholine', ['SER7b', 'ACM#2', 'GLR#8']).
neuron(146, 'M5', 'Acetylcholine', ['GLR#8']).
neuron(147, 'MCL', 'Acetylcholine', ['GLR#8', 'SER#7']).
neuron(148, 'MCR', 'Acetylcholine', ['GLR#8', 'SER#7']).
neuron(149, 'MI', 'null', ['GLR#2 ']).
neuron(150, 'NSML', 'Serotonin', ['GLR#7', 'GLR#8', 'SER#2', 'AEX#2']).
neuron(150, 'NSML', 'Glutamate', ['GLR#7', 'GLR#8', 'SER#2', 'AEX#2']).
neuron(151, 'NSMR', 'Serotonin', ['GLR#7', 'GLR#8', 'SER#2', 'AEX#2']).
neuron(151, 'NSMR', 'Glutamate', ['GLR#7', 'GLR#8', 'SER#2', 'AEX#2']).
neuron(152, 'OLLL', 'Glutamate', ['SER#2']).
neuron(153, 'OLLR', 'Glutamate', ['SER#2']).
neuron(154, 'OLQDL', 'Glutamate', ['OSM#9', 'OCR#4', 'NPR#1']).
neuron(155, 'OLQDR', 'Glutamate', ['OSM#9', 'OCR#4', 'NPR#1']).
neuron(156, 'OLQVL', 'Glutamate', ['OSM#9', 'OCR#4', 'NPR#1']).
neuron(157, 'OLQVR', 'Glutamate', ['OSM#9', 'OCR#4', 'NPR#1']).
neuron(158, 'PDA', 'null', ['EXP#1', 'UNC#8', 'SER#2']).
neuron(159, 'PDB', 'FMRFamide', ['UNC#8']).
neuron(160, 'PDEL', 'Dopamine', ['DOP#2']).
neuron(161, 'PDER', 'Dopamine', ['DOP#2']).
neuron(162, 'PHAL', 'null', ['GCY#12', 'OSM#9', 'OCR#2', 'SRG#13', 'SRB#6', 'NPR#1']).
neuron(163, 'PHAR', 'null', ['GCY#12', 'OSM#9', 'OCR#2', 'SRG#13', 'SRB#6', 'NPR#1']).
neuron(164, 'PHBL', 'Serotonin', ['OSM#9', 'OCR#2', 'SRB#6', 'NPR#1']).
neuron(165, 'PHBR', 'Serotonin', ['OSM#9', 'OCR#2', 'SRB#6', 'NPR#1']).
neuron(166, 'PHCL', 'null', ['DOP#1']).
neuron(167, 'PHCR', 'null', ['DOP#1']).
neuron(168, 'PLML', 'Glutamate', ['MEC#2', 'MEC#4', 'MEC#6', 'MEC#9DES#2', 'DOP#1']).
neuron(169, 'PLMR', 'Glutamate', ['MEC#2', 'MEC#4', 'MEC#6', 'MEC#9', 'DES#2', 'DOP#1']).
neuron(170, 'PLNL', 'Acetylcholine', ['DOP#1', 'GCY#35']).
neuron(171, 'PLNR', 'Acetylcholine', ['DOP#1', 'GCY#35']).
neuron(172, 'PQR', 'null', ['GCY#32', 'NPR#1', 'GCY#35 ']).
neuron(173, 'PVCL', 'null', ['DEG#3', 'SER#2']).
neuron(174, 'PVCR', 'null', ['DEG#3', 'SER#2']).
neuron(175, 'PVDL', 'Glutamate', ['MEC#10', 'MEC#9', 'MEC#6', 'OSM#9', 'SER#2', 'DEG#3', 'DOP#3']).
neuron(176, 'PVDR', 'Glutamate', ['MEC#10', 'MEC#9', 'MEC#6', 'OSM#9', 'SER#2', 'DEG#3', 'DOP#3']).
neuron(177, 'PVM', 'null', ['GAR#1', 'MEC#2', 'MEC#4', 'MEC#10', 'MEC#9']).
neuron(178, 'PVNL', 'null', ['null']).
neuron(179, 'PVNR', 'null', ['null']).
neuron(180, 'PVPL', 'null', ['null']).
neuron(181, 'PVPR', 'null', ['null']).
neuron(182, 'PVQL', 'null', ['GLR#1', 'GLR#5', 'SRA#6', 'DOP#1', 'GGR#1']).
neuron(183, 'PVQR', 'null', ['GLR#1', 'GLR#5', 'SRA#6', 'DOP#1', 'GGR#1']).
neuron(184, 'PVR', 'Glutamate', ['GGR#1']).
neuron(185, 'PVT', 'null', ['SER#2', 'SER#4']).
neuron(186, 'PVWL', 'null', ['null']).
neuron(187, 'PVWR', 'null', ['null']).
neuron(188, 'RIAL', 'null', ['Glr#3', 'GLR#6', 'SER#2']).
neuron(189, 'RIAR', 'null', ['Glr#3', 'GLR#6', 'SER#2']).
neuron(190, 'RIBL', 'null', ['DOP#1']).
neuron(191, 'RIBR', 'null', ['DOP#1']).
neuron(192, 'RICL', 'Octapamine', ['DOP#3', 'SER#2']).
neuron(193, 'RICR', 'Octapamine', ['DOP#3', 'SER#2']).
neuron(194, 'RID', 'GABA', ['EXP#1', 'SER#2']).
neuron(195, 'RIFL', 'null', ['null']).
neuron(196, 'RIFR', 'null', ['null']).
neuron(197, 'RIGL', 'FRMFemide', ['null']).
neuron(198, 'RIGR', 'FRMFemide', ['null']).
neuron(199, 'RIH', 'Serotonin', ['null']).
neuron(200, 'RIML', 'Tyramine', ['DOP#1']).
neuron(200, 'RIML', 'Acetylcholine', ['DOP#1']).
neuron(201, 'RIMR', 'Tyramine', ['DOP#1']).
neuron(201, 'RIMR', 'Acetylcholine', ['DOP#1']).
neuron(202, 'RIPL', 'Serotonin', ['null']).
neuron(203, 'RIPR', 'Serotonin', ['null']).
neuron(204, 'RIR', 'null', ['null']).
neuron(205, 'RIS', 'GABA', ['GLR#1', 'SER#4', 'DOP#1']).
neuron(206, 'RIVL', 'null', ['null']).
neuron(207, 'RIVR', 'null', ['null']).
neuron(208, 'RMDDL', 'Acetylcholine', ['null']).
neuron(209, 'RMDDR', 'Acetylcholine', ['null']).
neuron(210, 'RMDL', 'Acetylcholine', ['null']).
neuron(211, 'RMDR', 'Acetylcholine', ['null']).
neuron(212, 'RMDVL', 'Acetylcholine', ['null']).
neuron(213, 'RMDVR', 'Acetylcholine', ['null']).
neuron(214, 'RMED', 'GABA', ['AVR#15', 'SER#2']).
neuron(215, 'RMEL', 'GABA', ['GLR#1', 'SER#2']).
neuron(216, 'RMER', 'GABA', ['GLR#1', 'SER#2']).
neuron(217, 'RMEV', 'GABA', ['AVR#15', 'SER#2']).
neuron(218, 'RMFL', 'null', ['null']).
neuron(219, 'RMFR', 'null', ['null']).
neuron(220, 'RMGL', 'FRMFemide', ['null']).
neuron(221, 'RMGR', 'FRMFemide', ['null']).
neuron(222, 'RMHL', 'null', ['null']).
neuron(223, 'RMHR', 'null', ['null']).
neuron(224, 'SAADL', 'Acetylcholine', ['null']).
neuron(225, 'SAADR', 'Acetylcholine', ['null']).
neuron(226, 'SAAVL', 'Acetylcholine', ['null']).
neuron(227, 'SAAVR', 'Acetylcholine', ['null']).
neuron(228, 'SABD', 'Acetylcholine', ['EXP#1', 'SER#2']).
neuron(229, 'SABVL', 'Acetylcholine', ['DEL#1', 'SER#2']).
neuron(230, 'SABVR', 'Acetylcholine', ['DEL#1', 'SER#2']).
neuron(231, 'SDQL', 'Acetylcholine', ['GCY#35', 'SER#2']).
neuron(232, 'SDQR', 'Acetylcholine', ['GCY#35', 'SER#2']).
neuron(233, 'SIADL', 'Acetylcholine', ['DOP#3', 'GGR#3', 'GGR#2', 'SER#2']).
neuron(234, 'SIADR', 'Acetylcholine', ['DOP#3', 'GGR#3', 'GGR#2', 'SER#2']).
neuron(235, 'SIAVL', 'Acetylcholine', ['GGR#2', 'DOP#3', 'SER#2']).
neuron(236, 'SIAVR', 'Acetylcholine', ['GGR#2', 'DOP#3', 'SER#2']).
neuron(237, 'SIBDL', 'Acetylcholine', ['null']).
neuron(238, 'SIBDR', 'Acetylcholine', ['null']).
neuron(239, 'SIBVL', 'Acetylcholine', ['null']).
neuron(240, 'SIBVR', 'Acetylcholine', ['null']).
neuron(241, 'SMBDL', 'Acetylcholine', ['null']).
neuron(242, 'SMBDR', 'Acetylcholine', ['null']).
neuron(243, 'SMBVL', 'Acetylcholine', ['null']).
neuron(244, 'SMBVR', 'Acetylcholine', ['null']).
neuron(245, 'SMDDL', 'Acetylcholine', ['GGR#2', 'GGR#3']).
neuron(246, 'SMDDR', 'Acetylcholine', ['GGR#2', 'GGR#3']).
neuron(247, 'SMDVL', 'Acetylcholine', ['GGR#1', 'GGR#2']).
neuron(248, 'SMDVR', 'Acetylcholine', ['GGR#1', 'GGR#2']).
neuron(249, 'URADL', 'Acetylcholine', ['null']).
neuron(250, 'URADR', 'Acetylcholine', ['null']).
neuron(251, 'URAVL', 'Acetylcholine', ['null']).
neuron(252, 'URAVR', 'Acetylcholine', ['null']).
neuron(253, 'URBL', 'Acetylcholine', ['null']).
neuron(254, 'URBR', 'Acetylcholine', ['null']).
neuron(255, 'URXL', 'null', ['GCY#32', 'GCY#35', 'NPR#1', 'SRA#10']).
neuron(256, 'URXR', 'null', ['GCY#32', 'GCY#35', 'NPR#1', 'SRA#10']).
neuron(257, 'URYDL', 'null', ['null']).
neuron(258, 'URYDR', 'null', ['null']).
neuron(259, 'URYVL', 'null', ['null']).
neuron(260, 'URYVR', 'null', ['null']).
neuron(261, 'VA1', 'Acetylcholine', ['DEL#1']).
neuron(262, 'VA10', 'Acetylcholine', ['DEL#1']).
neuron(263, 'VA11', 'Acetylcholine', ['DEL#1']).
neuron(264, 'VA12', 'Acetylcholine', ['DEL#1']).
neuron(265, 'VA2', 'Acetylcholine', ['DEL#1']).
neuron(266, 'VA3', 'Acetylcholine', ['DEL#1']).
neuron(267, 'VA4', 'Acetylcholine', ['DEL#1']).
neuron(268, 'VA5', 'Acetylcholine', ['DEL#1']).
neuron(269, 'VA6', 'Acetylcholine', ['DEL#1']).
neuron(270, 'VA7', 'Acetylcholine', ['DEL#1']).
neuron(271, 'VA8', 'Acetylcholine', ['DEL#1']).
neuron(272, 'VA9', 'Acetylcholine', ['DEL#1']).
neuron(273, 'VB1', 'Acetylcholine', ['DEL#1']).
neuron(274, 'VB10', 'Acetylcholine', ['DEL#1']).
neuron(275, 'VB11', 'Acetylcholine', ['DEL#1']).
neuron(276, 'VB2', 'Acetylcholine', ['DEL#1']).
neuron(277, 'VB3', 'Acetylcholine', ['DEL#1']).
neuron(278, 'VB4', 'Acetylcholine', ['DEL#1']).
neuron(279, 'VB5', 'Acetylcholine', ['DEL#1']).
neuron(280, 'VB6', 'Acetylcholine', ['DEL#1']).
neuron(281, 'VB7', 'Acetylcholine', ['DEL#1']).
neuron(282, 'VB8', 'Acetylcholine', ['DEL#1']).
neuron(283, 'VB9', 'Acetylcholine', ['DEL#1']).
neuron(284, 'VC1', 'Acetylcholine', ['GLR#5']).
neuron(284, 'VC1', 'Serotonin', ['GLR#5']).
neuron(285, 'VC2', 'Acetylcholine', ['GLR#5']).
neuron(285, 'VC2', 'Serotonin', ['GLR#5']).
neuron(286, 'VC3', 'Acetylcholine', ['GLR#5']).
neuron(286, 'VC3', 'Serotonin', ['GLR#5']).
neuron(287, 'VC4', 'Acetylcholine', ['GLR#5']).
neuron(287, 'VC4', 'Serotonin', ['GLR#5']).
neuron(288, 'VC5', 'Acetylcholine', ['GLR#5']).
neuron(288, 'VC5', 'Serotonin', ['GLR#5']).
neuron(289, 'VC6', 'Acetylcholine', ['GLR#5']).
neuron(289, 'VC6', 'Serotonin', ['GLR#5']).
neuron(290, 'VD1', 'GABA', ['NPR#1']).
neuron(291, 'VD10', 'GABA', ['NPR#1']).
neuron(292, 'VD11', 'GABA', ['NPR#1']).
neuron(293, 'VD12', 'GABA', ['NPR#1']).
neuron(294, 'VD13', 'GABA', ['NPR#1']).
neuron(295, 'VD2', 'GABA', ['NPR#1']).
neuron(296, 'VD3', 'GABA', ['NPR#1']).
neuron(297, 'VD4', 'GABA', ['NPR#1']).
neuron(298, 'VD5', 'GABA', ['NPR#1']).
neuron(299, 'VD6', 'GABA', ['NPR#1']).
neuron(300, 'VD7', 'GABA', ['NPR#1']).
neuron(301, 'VD8', 'GABA', ['NPR#1']).
neuron(302, 'VD9', 'GABA', ['NPR#1']).


%TRANSMITTERS:
process_missing_transmitters:-
	neuron(_ID, OrigNeuron, _NT, _L),
	findall(Receptors, (synapse(OrigNeuron, RNeuron, _), neuron(_, RNeuron, 'null', Receptors)), RNs),
	prepare_element_list(RNs, RNNew),
	correspond_transmitter(RNNew, PossibleTransmitters),
	output_nicely(OrigNeuron, PossibleTransmitters),
	fail.
process_missing_transmitters.

correspond_transmitter(RNs, TRs):-
	correspond_transmitter(RNs, [], TRsTemp),
	flatten(TRsTemp, TRs).
correspond_transmitter([], TRs, TRs).
correspond_transmitter([H|T], AccTRs, TRs):-
	findall(Transmitter, transmit_recept(Transmitter, H, _), Transmitters),
	correspond_transmitter(T, [Transmitters| AccTRs], TRs).

%RECEPTORS:
process_missing_receptors:-
	neuron(_ID, OrigNeuron, _NT, _L),
	findall(Transmitter, (synapse(OrigNeuron, RNeuron, _), neuron(_, RNeuron, Transmitter, ['null'])), TRs),
	prepare_element_list(TRs, TRNew),
	correspond_receptor(TRNew, PossibleReceptors),
	output_nicely(OrigNeuron, PossibleReceptors),
	fail.
process_missing_receptors.

correspond_receptor(TRs, RNs):-
	correspond_receptor(TRs, [], RNsTemp),
	flatten(RNsTemp, RNs).
correspond_receptor([], TRs, TRs).
correspond_receptor([H|T], AccTRs, TRs):-
	findall(Receptor, transmit_recept(H, Receptor, _), Receptors),
	correspond_receptor(T, [Receptors| AccTRs], TRs).

%GENERAL FUNCTIONS:
prepare_element_list(RNs, RNNew):-
	flatten(RNs, RNFlat),
	prepare_element_list(RNFlat, [], RNNew).

prepare_element_list([], L, L).
prepare_element_list([H|T], AccList, RNnew):-
	\+ memberchk(H, AccList),  !,
	prepare_element_list(T, [H|AccList], RNnew).
prepare_element_list([H|T], AccList, RNnew):-
	prepare_element_list(T, AccList, RNnew).

count(Nj, L, C):-
	count(Nj, L, C, 0).
count(_Nj, [], C, C):-!.
count(Nj, [H| T], CountNj, Acc):-
	(Nj == H ->
		AccNew is Acc + 1
	;
		AccNew is Acc
	),
	count(Nj, T, CountNj, AccNew).

counted_single_list(Orig, Res):-
	csl(Orig, [], [], Res).

csl([], _, Res, Res):-!.
csl([H|T], SeenList, AccCountedList, Res):-
	\+ memberchk(H, SeenList), !,
	count(H, T, C),
	C_and_self is C+1,
	csl(T, [H|SeenList], [[H,C_and_self]| AccCountedList], Res).
csl([H|T], SeenList, AccCountedList, Res):-
	memberchk(H, SeenList),
	csl(T, SeenList, AccCountedList, Res).

output_nicely(Neuron, PossibleTransmitters):-
	write('--For neuron '), write(Neuron), writeln(': '),
	counted_single_list(PossibleTransmitters, CountedList),
	printout_nicely(CountedList),
	write('--END of neuron '), writeln(Neuron).

printout_nicely([]).
printout_nicely([[Transmitter, Count]|Rest]):-
	write(Transmitter), write(' - '), writeln(Count),
	printout_nicely(Rest).


:-writeln('Processing Unknown Transmitters:'), process_missing_transmitters.
:-writeln('').
:-writeln('Processing Unknown Receptors:'), process_missing_receptors.
