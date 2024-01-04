echo "Checking for repeating byes"
cat /tmp/t | awk '{print $(NF-2), $(NF-1), $NF}' | tr "," "\n" | sed 's/ //' | sort -n  | uniq -c | sed 's/      //' | grep -v ^1


echo "Checking for repeating players in each round"
for line in `cat /tmp/t`; do echo $line |tr "," "\n" | grep [0-9] | sort -n | uniq -c; done | sed 's/      //' | grep -v ^1

echo "Checking for repeated partner pairs"
cat /tmp/t | tr "\t" "\n"| grep vs | tr " " "\n" | grep [0-9] | sort -n | uniq -c | sed 's/      //' | grep -v 1





