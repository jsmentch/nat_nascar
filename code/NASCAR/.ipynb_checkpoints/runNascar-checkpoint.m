%clear; close all; clc;

function [Y2, R] = runNascar(input_file, R)

    % Use the fileparts function to extract the filename
    [path, filename, ext] = fileparts(input_file);

    % put the directory of the downloaded folder below or just switch to that folder in Matlab
    mainDir = pwd;
    addpath(fullfile(mainDir, 'dependency'));
    addpath(fullfile('../GroupBrainSync'));
    addpath(fullfile('../GroupBrainSync/dependency'));
    %addpath(fullfile('../../data'))

    disp('added paths')

    data=h5read(input_file,'/data');
    
    disp('read h5')

    N = size(data, 3); %voxel
    T = size(data, 2); %time
    S = size(data, 1); %subject
    disp([ N T S])
    
    data= permute(data, [3, 2, 1]); % make data N(V) x T x S for nascar
    
    data2 = permute(data, [2, 1, 3]); % make data2 T x V x S for GBS (time, voxel, subject)
    
    disp('start GBS')
    
    %% Group BrainSync
    option = groupBrainSync();
    %option.numCPU = 8;
    option.epsX = 2e-3
    [Y, O] = groupBrainSync(data2, option);
    save(['../../data/nascar_output/' filename '_GBS.mat'],'Y', 'O');

    %% BrainSync temporal alignment
    for m = 1:S
        data(:, :, m) = brainSyncT(Y', data(:, :, m));
        m
    end

    %% NASCAR algorithm (use opt inside srscpd framework)
    option = srscpd('opt');
    %option.nonnegative = [0 0 1];
    option.rankOneOptALS.useTFOCS = false; % if use TFOCS or not to solve rank 1 problem
    option.optAlg.normRegParam = 0.001; % regularization parameter on the norm of each mode
    option.optAlg.optSolver.printItv = 10; % print interval
    option.optAlg.optSolver.learningRate = 1e-3; % Nadam learning rate
    option.optAlg.optSolver.maxNumIter = 2000; % max number of iterations in Nadam
    option.optAlg.cacheMTS = true; % turn this on if you have enough memory to speed up
    % save result at the end of each iteration during the decomposition
    % option.saveToFile = ['../../data/nascar_output/' filename '_working.mat'];

    % save logs (what printed in the command window) to a file
    option.logFile = ['../../data/nascar_output/' filename '_log'];

    % if NASCAR paused or is interrupted for some reason, it can be resumed
    % by providing the results from lower ranks
    % option.resumeFrom = ['../../data/nascar_output/' filename '_working.mat'];

    result = srscpd(data, R, option);

    %% the decomposition results are stored in U
    U2 = result(R).U;
    lambda2 = result(R).Lambda;

    %save NASCAR results
    %save('../../data/nascar_output/ru_rest_results.mat', 'U2', 'lambda2');
    save(['../../data/nascar_output/' filename '_results.mat'], 'U2', 'lambda2');
    
    exit
end