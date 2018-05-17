origWorkingDir=$(pwd)
py.test --cov="$origWorkingDir" --cov-report term --cov-report html:"$origWorkingDir"/htmlcov
