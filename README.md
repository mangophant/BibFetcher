# BibFetcher: Fetching bibtex from dblp with title/author information automatically

*BibFetcher* is designed to automatically fetch bittex for CS articles and proceedings, with only the title information (or plus some authors), e.g.,

given:
```json
{
    "resnet": "Deep Residual Learning for Image Recognition, Kaiming He"
}
```

fetch bibtex for latex users:
```bibtex
@inproceedings{resnet,
	author= {Kaiming He, Xiangyu Zhang, Shaoqing Ren and Jian Sun},
	title= {{Deep Residual Learning For Image Recognition}},
	booktitle= {Proceedings of {IEEE} {CVPR}},
	pages= {770-778},
	address= {Las Vegas, NV, USA},
	year= {2016},
}
```

or text for Mircosoft Word users:
```
Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun, "Deep Residual Learning For Image Recognition", in Proceedings of IEEE CVPR, pp.770-778, Las Vegas, NV, USA, 2016.
```

## Requirements
```
Requests==2.31.0
beautifulsoup4==4.12.3
```

## Usage
`python main.py [-h] [-i INPUT_JSON_FILE] [-o OUTPUT_BIB_OR_TXT_FILE] [-l LOG_FILE] [-t TIME_SLEEP] [-n NUM_FETCH] [-k]`
```
Import bibliography entries from DBLP.

options:
  -h, --help            show this help message and exit
  -i INPUT_JSON_FILE, --input INPUT_JSON_FILE
                        File name of input .json file with columns [citekey, title, author<optional>]
  -o OUTPUT_BIB_OR_TXT_FILE, --output OUTPUT_BIB_OR_TXT_FILE
                        File name of output .bib or .txt file
  -l LOG_FILE, --logfile LOG_FILE
                        File name of the logging file
  -t TIME_SLEEP, --time_sleep TIME_SLEEP
                        Sleep interval between two queries
  -n NUM_FETCH, --num_fetch NUM_FETCH
                        Maximum number of fetching for each entry
  -k, --keep_empty_field
                        Output empty field in the bib entry or not
```

## Test example
- Create and activate a virtual environment, download python and the required packages.
- Check the file `ref.json` to know about the input format.
- Run the follow command and you can derive `ref.bib` or `ref.txt` with detailed logs in `ref.log`:
```
python main.py -i ref.json -o ref.bib -l ref.log -t 2 -n 3 -k
python main.py -i ref.json -o ref.txt -l ref.log -t 3 -n 3
```

## Tips
1. The citation key in the `ref.json` file can be customized for quick autocompletion to browse references.
2. Make sure the query information (title, or title + author) is accurate, otherwise no bib entry will be matched, as you search on the DBLP website.
3. Don't forget to check the `ref.log` file to corret the incomplete entries, which may **miss** fields or include **empty** fields.
4. For entries failed to fetch (due to the HTTP query limitation of dblp), wait for seconds, and run BibFetcher on them again with a larger sleep interval between queries. Repeat this until it meets your requirement.
5. Sometime there are multiple bib entries matching the query. To ensure the correct bib is fetched, you need to manually select one of them by navigating the candidate page or just keep it empty, e.g., given the query string "generative adversarial network", the candidate page looks like:
```
main.py line:48 INFO Entry: [  1/  1] gan                    Try: (1/3) >> Found
>> Multiple entry matched:

(0) Keep Empty

(1) Title: ARGAN: Adversarially Robust Generative Adversarial Networks for Deep Neural Networks Against Adversarial Examples.
    Auhtor: SeokHwan Choi, Jin-Myeong Shin, Peng Liu, Yoon-Ho Choi
    Venue: IEEE Access 2022

(2) Title: Network intrusion detection based on conditional wasserstein variational autoencoder with generative adversarial network and one-dimensional convolutional neural networks.
    Auhtor: Jiaxing He, Xiaodan Wang, Yafei Song, Qian Xiang, Chen Chen
    Venue: Appl. Intell. 2023

(3) Title: RegraphGAN: A graph generative adversarial network model for dynamic network anomaly detection.
    Auhtor: Dezhi Guo, Zhaowei Liu, Ranran Li
    Venue: Neural Networks 2023

(4) Title: Improved Residual Dense Network for Large Scale Super-Resolution via Generative Adversarial Network.
    Auhtor: Inad A. Aljarrah, Eman M. Alshare
    Venue: Int. J. Commun. Networks Inf. Secur. 2022

(5) Title: Fast and computationally efficient generative adversarial network algorithm for unmanned aerial vehicle-based network coverage optimization.
    Auhtor: Marek Ruzicka, Marcel Volosin, Juraj Gazda, Taras Maksymyuk, Longzhe Han, Mischa Dohler
    Venue: Int. J. Distributed Sens. Networks 2022

(u) Page Up | Page  1/ 6 | (d) Page Down

>> Choose candidate or navigate page:
```

## Venues
Check the supported venues in `venue.py/venue_dict`. You can customize their abbreviations that appear in the bibtex or add more venues.

> Note that BibFetcher only supports conference, journal, and arXiv papers currently, other types of publications, e.g., book, will be passed.

## Contributors
- [Meng Chen](https://czyxm.github.io)
- [Kun Wang](https://github.com/kuang22)