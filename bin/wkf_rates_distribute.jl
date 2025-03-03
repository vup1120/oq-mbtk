#!/usr/bin/env julia

using Glob
using ArgParse
using Printf
using PSHAModelBuilder
using TOML


function distribute_rates(folder_smooth, fname_config, folder_out)

    # Parse the configuration file
	config = TOML.parsefile(fname_config)
	
    # Loop over the zones
	pattern = joinpath(folder_smooth, "*.csv")
	for tmps in glob(pattern)
		fname = splitdir(tmps)[2]
		source_id = split(fname, '.')[1]
		agr = config["sources"][source_id]["agr"]
		bgr = config["sources"][source_id]["bgr"]
		fname_out = joinpath(folder_out, @sprintf("%s.csv", source_id))
		PSHAModelBuilder.distribute_total_rates(agr, bgr, tmps, fname_out)
	end
		
end

function parse_commandline()
    s = ArgParseSettings()

    @add_arg_table s begin
        "smooth_folder"
            help = "name of the .csv file produced by box counting"
			arg_type = String
			required = true
        "config"
            help = "name of the .toml configuration file"
			arg_type = String
            required = true
		"folder_out"
		    help = "Folder where to save output files"
			arg_type = String
		    required = true
    end

    return parse_args(s)
end


function main()
	
	# Parsing command line args
    args = parse_commandline()

	# Creating output folder
	if !isdir(args["folder_out"])
		mkpath(args["folder_out"])
	end

	# Running smoothing
	distribute_rates(args["smooth_folder"], args["config"], args["folder_out"])

end

main()
