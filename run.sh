# Generate Files
if [ $# -eq 0 ]
  then
    echo "No parameters provided. Launching bash"
    bash
else
    while test $# -gt 0; do
      case "$1" in
        -h|--help)
          echo "$package [options] application [arguments]"
          echo " "
          echo "options:"
          echo "-h, --help                show brief help"
          echo "-c,                       launch clustering"
          echo "-m,                       launch mapping"
          exit 0
          ;;
        -c)
          echo "Copying custom input file if exists..."
          if [ -f /home/input_clustering.py ]; then
            mv /home/input_clustering.py /home/cogomo/input_clustering.py
            echo "Custom input file loaded"
          fi
          echo "Launching clustering..."
          python3 ./run_clustering.py
          echo "Process finished, results avilable"
          exit 0
          ;;
        -m)
          echo "Launching mapping..."
          python3 ./run_mapping.py
          exit 0
          ;;
        *)
          break
          ;;
      esac
    done
fi
