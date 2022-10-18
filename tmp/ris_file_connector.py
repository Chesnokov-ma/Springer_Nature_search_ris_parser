from os import walk


# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
filenames = next(walk('./'), (None, None, []))[2]

output_str = ''

for file in filenames:
    with open(file, 'r', encoding='utf-8') as f:        # read all files in download dir
        output_str += (f.read() + '\n')

with open('../res_file.ris', 'w', encoding='utf-8') as of:      # write to file with all refs
    of.write(output_str)

print(f'Data collected in ../res_file.ris')