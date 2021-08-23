import click
import urllib
import sys
import requests

from concurrent.futures import as_completed, ThreadPoolExecutor
from tqdm import tqdm
from colorama import Fore, Style
from dataclasses import dataclass


def _print_banner():
    banner = Fore.RED + """\n                                                                                      
  iiii  BBBBBBBBBBBBBBBBB                                               tttt          
 i::::i B::::::::::::::::B                                           ttt:::t          
  iiii  B::::::BBBBBB:::::B                                          t:::::t          
        BB:::::B     B:::::B                                         t:::::t          
iiiiiii   B::::B     B:::::Buuuuuu    uuuuuu      ssssssssss   ttttttt:::::ttttttt    
i:::::i   B::::B     B:::::Bu::::u    u::::u    ss::::::::::s  t:::::::::::::::::t    
 i::::i   B::::BBBBBB:::::B u::::u    u::::u  ss:::::::::::::s t:::::::::::::::::t    
 i::::i   B:::::::::::::BB  u::::u    u::::u  s::::::ssss:::::stttttt:::::::tttttt    
 i::::i   B::::BBBBBB:::::B u::::u    u::::u   s:::::s  ssssss       t:::::t          
 i::::i   B::::B     B:::::Bu::::u    u::::u     s::::::s            t:::::t          
 i::::i   B::::B     B:::::Bu::::u    u::::u        s::::::s         t:::::t          
 i::::i   B::::B     B:::::Bu:::::uuuu:::::u  ssssss   s:::::s       t:::::t    tttttt
i::::::iBB:::::BBBBBB::::::Bu:::::::::::::::uus:::::ssss::::::s      t::::::tttt:::::t
i::::::iB:::::::::::::::::B  u:::::::::::::::us::::::::::::::s       tt::::::::::::::t
i::::::iB::::::::::::::::B    uu::::::::uu:::u s:::::::::::ss          tt:::::::::::tt
iiiiiiiiBBBBBBBBBBBBBBBBB       uuuuuuuu  uuuu  sssssssssss              ttttttttttt  
                                                                                      \n"""
    banner += Fore.BLUE + '\tHome made DirBuster in python3\n' + Style.RESET_ALL
    banner += Fore.GREEN + '\tVersion 1.0.\n' + Style.RESET_ALL
    banner += Fore.WHITE + '\tHosted on https://github.com/iftachFridental/ibust\n\n' + Style.RESET_ALL
    print(banner)


def _print_err(message):
	sys.stderr.write(Fore.RED + '[X]'+Style.RESET_ALL+'\t%s\n' % message)


def _print_succ(message):
	sys.stdout.write(Fore.GREEN + '[+]'+Style.RESET_ALL+'\t%s\n' % message)


def _print_info(message):
	sys.stdout.write(Fore.BLUE + '[+]' + Style.RESET_ALL + '\t%s\n' % message)


@click.command(no_args_is_help=True)
@click.option(
    '-u',
    '--url',
    required=True,
    help='full url with scheme to start from')
@click.option(
    '-p',
    '--port',
    default=None,
    help='port to request to'
)
@click.option(
    '-l',
    '--dictfile',
    required=True,
    help='dict list file to bruteforce'
)
@click.option(
    '-o',
    '--outfile',
    default='scan_result.txt',
    help='out file to save results'
)
def main(url, port, dictfile, outfile):
    try:
        _print_banner()
        
        parsed_url = urllib.parse.urlparse(url)
        scheme = parsed_url.scheme if parsed_url.scheme in ['http', 'https'] else 'https'
        final_port = port if port else (parsed_url.port if parsed_url.port else '443')
        final_url = f'{scheme}://{parsed_url.hostname}:{final_port}{parsed_url.path}'

        dirbust(
            starting_point_url=final_url, 
            dirlist_path=dictfile,
            result_path=outfile
        )

        _print_succ('Done!')
    
    except KeyboardInterrupt:
        _print_info('Exitting...')


@dataclass
class RequestResult:
    status_code: int
    success: bool
    url: str


def do_get(url):
    try:
        response = requests.get(
            url,
            timeout=2
        )
    except Exception as e:
        _print_err(str(e))
        return RequestResult(
            status_code=-1,
            success=False,
            url=url
        )
    scode = response.status_code
    return RequestResult(
        status_code=scode,
        success=(200 <= scode <= 300),
        url=url
    )


def dirbust(
    starting_point_url,
    dirlist_path,
    result_path
    ):
    '''dir bust to discover directory files and subdirectories'''
    
    with open(dirlist_path, 'r') as dirlist_file:
        bust_urls = [
            f'{starting_point_url}{diropt.strip()}'
            for diropt in dirlist_file.readlines()
        ]

    with open(result_path, 'w') as result_file:
        with tqdm(total=len(bust_urls)) as pbar:
            with ThreadPoolExecutor(max_workers=len(bust_urls)) as executor:
                futures = [
                    executor.submit(do_get, url)
                    for url in bust_urls
                ]
                for future in as_completed(futures):
                    result = future.result()
                    result_file.write(f'{"EXIST" if result.success else "NOT FOUND"} (status code: {result.status_code}) @ {result.url}\n')
                    pbar.update(1)

if __name__ == '__main__':
    main()
