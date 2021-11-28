from setuptools import setup


with open('README.md', 'r') as f:
    readme = f.read()


setup(name='daemonlib',
      version='1.5.0',
      description="Daemonization library and other utilities",
      url='http://gitlab.com/atkozhuharov/daemonlib',
      Author='Atanas K',
      author_email='atkozhuharov@gmail.com',
      license='MIT',
      packages=['daemonlib'],
      python_requires='>3.6',
      install_requires=['psutil>=5.4.8'],
      zip_safe=False)
