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
          echo "Launching clustering..."
          python3 ./clustering_run.py
          ;;
        -m)
          echo "Launching mapping..."
          python3 ./mapping_run.py
          ;;
        *)
          break
          ;;
      esac
    done
fi
