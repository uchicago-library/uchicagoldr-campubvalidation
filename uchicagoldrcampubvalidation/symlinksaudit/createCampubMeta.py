from uchicagoldr.collection import Collection
from uchicagoldr.batch import AccessionDirectory
from uchicagoldr.batch import Batch

accessions = ['j99fm7wmsznwr', '8ss4zsz1qxgx4', '5k6f554szkjtp',
              '2mn4w1c38cq4t', 'jsrfb0tc9tvff', 'gfvv98j8j5wcn',
              'zw4xczwm89dkq', 'hpctwgwbd4kkb', 'wh503589sj5hh',
              'fqpgj2vbd5jv6', '16r5hf53f045t', '4bhmpwjcnfsc5',
              'wf13zxt7k408j', 'bqrhbgxr1tp4x', 's9gx23kjrzvh8',
              '9xbpbx4z3s0v3', '8rvz3dbzd3s2j', 't8xzfqfx07k74',
              'vbd22dxrxr5xw', '17w1z2v4fjcz0', '8sm8f7n01m3k5',
              'nfgwxqrv2m4rr', 'jwpmn1p86szg7', 'j4r6schrjnv62',
              'xg33bt6bk3k7s', 'pr9fjs2dtn4pj', '0wh19dztggpd8',
              'r089znx8pc4fm', '7d331rcvjncrr', 'n4cg28cnz5sc3',
              'kz8zsx188hzr3', '56pk8ggqvqs2v', '2036zz1q99cp6',
              'j7w806c9xbsb0', 't6ggdbf3fgdk2', 'psccz8dqk3c2d',
              '5gcq3n8pxjzsw', 'fqr6nc9bvzmb1', 'cfjgj31g02gg0',
              '6v70z39j9vgc2', '2s71kqkg89fgq', 'mr4bj958qs5dc',
              'j7nt8hx3hwzd5']

accessionDirectories = []

counter=0
for accession in accessions:
    counter += 1
    print(str(counter)+'/'+str(len(accessions)))
    accDir = AccessionDirectory('/Volumes/ac/'+accession, '/Volumes/ac/')

    try:
        for item in accDir.walk_directory_picking_files():
            accNo = item.get_file_path().split("/")[4]
            item.set_root_path(item.get_root_path() + "/" + item.get_accession() + "/" + accNo+"/")
            item.set_canonical_filepath(item.find_canonical_filepath()[3:])
            accDir.add_item(item)
        accessionDirectories.append(accDir)
    except FileNotFoundError:
        continue

camPub = Collection(accessionDirectories)

print("Creating meta-accession")
metaAccession = camPub.createMetaAccession()

print("Writing to file")
with open('campubmeta.txt', 'w') as f:
    for item in metaAccession:
        f.write(item.get_file_path() + "\n")
