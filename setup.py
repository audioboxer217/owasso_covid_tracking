from setuptools import setup, find_packages 

with open('requirements.txt') as f: 
	requirements = f.readlines() 

long_description = 'Tracking for COVID in Owasso area' 

setup( 
		name ='owasso_covid', 
		version ='1.0.0', 
		author ='Scott Eppler', 
		author_email ='audioboxer217@gmail.com', 
		url ='', 
		description ='Tracking for COVID in Owasso area', 
		long_description = long_description, 
		long_description_content_type ="text/markdown", 
		license ='MIT', 
		packages = find_packages(), 
		entry_points ={ 
			'console_scripts': [ 
				'update_covid_db = src.update_db:main',
        'generate_covid_graphs = src.generate_graphs.py'
			]
		}, 
		classifiers =( 
			"Programming Language :: Python :: 3", 
			"License :: OSI Approved :: MIT License", 
			"Operating System :: OS Independent", 
		), 
		keywords ='owasso covid', 
		install_requires = requirements, 
		zip_safe = False
) 
