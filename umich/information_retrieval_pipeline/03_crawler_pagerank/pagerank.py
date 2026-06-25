# Author

### imports
import sys

### main function 
def main():
    # check that the input of the command line is in the right format
    if len(sys.argv) != 4:
        print("The command line does not have the correct number of arguments")
        sys.exit(1)
    # initialize variables
    urls_file = sys.argv[1]
    links_file = sys.argv[2]
    threshold = float(sys.argv[3])
    # read urls and create mappings
    urls = []
    url_to_idx = {}
    # make url dictionary
    with open(urls_file, 'r') as f:
        for idx, line in enumerate(f):
            url = line.strip()
            urls.append(url)
            url_to_idx[url] = idx
    # initialize number of urls
    N = len(urls)
    # initialize in_links and out_degree to keep track of
    out_degree = {url: 0 for url in urls}
    in_links = {url: {} for url in urls}
    ## process links from links file
    with open(links_file, 'r') as f:
        # for each url in the links file
        for line in f:
            line = line.strip()
            if not line:
                continue
            # extract source and target from line formatted as (source, target)
            line = line.lstrip('(').rstrip(')')
            parts = line.split(', ')
            source = parts[0].strip()
            target = parts[1].strip()
            # check if both urls are valid
            if source not in url_to_idx or target not in url_to_idx:
                continue
            # update out_degree for source
            out_degree[source] += 1
            # update in_links for target
            if source in in_links[target]:
                in_links[target][source] += 1
            else:
                in_links[target][source] = 1

    ## initialize PageRank scores
    d = 0.85
    current_pr = [0.25] * N
    iteration = 0
    ## iterate until the scores reach the required treshold
    while True:
        next_pr = [0.0] * N
        for i in range(N):
            url = urls[i]
            sum_contribution = 0.0
            # sum contributions from all in_links
            sources = in_links.get(url, {})
            for source, count in sources.items():
                source_idx = url_to_idx[source]
                od = out_degree[source]
                if od == 0:
                    continue
                sum_contribution += (current_pr[source_idx] * count) / od
            # update PageRank value
            next_pr[i] = (1 - d) / N + d * sum_contribution

        max_diff = 0.0
        for i in range(N):
            # for testing only ---------------------------------------------
            # if urls[i] == "https://cse.engin.umich.edu/about/contact/":
            #     print(next_pr[i] - current_pr[1])
            # ---------------------------------------------------------------
            diff = abs(next_pr[i] - current_pr[i])
            if diff > max_diff:
                max_diff = diff
        if max_diff < threshold:
            break

        # prepare for next iteration
        current_pr = next_pr.copy()
        iteration += 1
    # print the number of iteration the algorithm took
    print(iteration)
    # sort urls by descending PageRank and then alphabetically
    sorted_pr = sorted(zip(urls, current_pr), key=lambda x: (-x[1], x[0]))

    # write to pagerank.output
    with open('pagerank.output', 'w') as f:
        f.write("Author \n \n")
        for url, score in sorted_pr:
            f.write(f"{url} {score}\n")

### main function
if __name__ == "__main__":
    # run main
    main()