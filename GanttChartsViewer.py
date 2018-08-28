# python3.6
# -*- coding: utf-8 -*-

import sys, io, getopt, random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# the format of instance seperated by i rows and j columns,
# each (i, j) represent the processing time of job j on machine i
def load_instance(filename):
	try:
		return np.genfromtxt(filename, delimiter=' ')
	except IOError:
		print('IOError: file ' + filename +' does not exist.')
		sys.exit(2)
	
# by changing the definition of beginning/ending time,
# it also can show the Gantt Chart of no-wait PFSP
def get_timetable(proc, seq):
	begin = np.empty((proc.shape[0], proc.shape[1]), 'int64')
	end = np.empty((proc.shape[0], proc.shape[1]), 'int64')
	for i in range(proc.shape[0]):
		if i == 0:
			begin[0, 0] = 0
			end[0, 0] = proc[0, seq[0]]
		else:
			begin[i, 0] = end[i-1, 0]
			end[i, 0] = begin[i, 0] + proc[i, seq[0]]

		for j in range(1, proc.shape[1]):
			if i == 0:
				begin[0, j] = end[0, j-1]
				end[0, j] = begin[0, j] + proc[0, seq[j]]
			else:
				begin[i, j] = max(end[i, j-1], end[i-1, j])
				end[i, j] = begin[i, j] + proc[i, seq[j]]
	return begin, end

def evaluate(begin, end):
	return end[-1, -1], end.sum(axis=1)[-1]

# return the infomation of beginning/ending time in the csv format
def get_timestring(begin, end):
	s = ''
	for i in range(begin.shape[0]):
		for j in range(begin.shape[1]):
			s += ('M' + str(i+1) + ',' + str(begin[i, j]) + ',' + str(end[i, j]) + ','
				  'J' + str(j+1) + '\n')
	return s

def random_color(n):
	r = lambda: random.randint(0,255)
	code = []
	for i in range(n):
		code.append("#{:02x}{:02x}{:02x}".format(r(),r(),r()))
	return code

def show_fig(filename, title, colors, save_figure, objectives=''):
	df = pd.read_csv(filename, header=None, names=["Machine", "Start", "Finish", "Job"] )
	df["Diff"] = df.Finish - df.Start
	num_machines = len(df.groupby("Machine"))
	num_jobs = len(df.groupby("Job"))

	df["Machine"] = pd.Categorical(df["Machine"], ['M'+str(i) for i in range(1, num_machines+1)])
	df = df.sort_values(by=["Machine"])

	fig, ax = plt.subplots(figsize=(10,5))
	ax.set_title(title)
	
	labels=[]
	for i, machine in enumerate(df.groupby("Machine")):
	    labels.append(machine[0])
	    for j in machine[1].groupby("Job"):
	    	data = j[1][["Start", "Diff"]]
	    	ax.broken_barh(data.values, (num_machines-1-i-0.4, 0.8), color=colors[j[0]], label=j[0], edgecolor='k', lw=0.8)
	    	
	ax.set_yticks(range(len(labels)))
	ax.set_yticklabels(reversed(labels))
	
	if save_figure and len(objectives) > 0:
		figure_name = '[' + str(objectives[0]) + ', ' + str(objectives[1]) + '].png'
		plt.savefig(figure_name, format='png')
	else:
		plt.show()

def show_gantt_charts(instance, sequence, save_figure=False):
	proc_time = load_instance(instance)
	if len(sequence) == 0:
		sequence = [n for n in range(proc_time.shape[1])]
		random.shuffle(sequence)
	
	rc = random_color(proc_time.shape[1])
	colors = {}
	for i in range(1, len(rc)+1):
		colors['J'+str(i)] = rc[i-1]

	begin, end = get_timetable(proc_time, sequence)
	objectives = evaluate(begin, end)

	ts = get_timestring(begin, end)
	title = 'MKS = '+str(objectives[0])+', TFT = '+str(objectives[1])
	show_fig(io.StringIO(ts), title, colors, save_figure, objectives)

def usage():
	print('\n\t*** Gantt Charts Viewer for PFSP ***\n')
	print('\tusage: -i <instance> [-p <permutations> -s]\n')
	print('\toptional arguments:')
	print('\t-p <permutations>: load permutations from file.')
	print('\t-s or --save: save gantt charts in the PNG format.')
	
def main():
	if len(sys.argv[1:]) > 0:
		try:
			opts, args = getopt.getopt(sys.argv[1:], "hi:p:s", ["help", "", "", "save"])
		except getopt.GetoptError as e:
			print('\nGetoptError: option not recognized.\n')
			usage()
			sys.exit(2)
	else:
		usage()
		sys.exit()

	instance = ''
	permutations = ''
	save_figure = False
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt == '-i':
			instance = arg
		elif opt == '-p':
			permutations = arg
		elif opt in ("-s", "--save"):
			save_figure = True

	if len(permutations) > 0:
		for line in open(permutations, 'r'):
			if ',' in line:
				p = [int(i) for i in line[:-1].split(', ')]
			else:
				p = [int(i) for i in line[:-1].split()]
			show_gantt_charts(instance, p, save_figure)
	else:
		show_gantt_charts(instance, '', save_figure)

if __name__ == "__main__":
	main()
