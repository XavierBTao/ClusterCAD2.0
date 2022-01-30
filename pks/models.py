import sys
from django.db import models
from model_utils.managers import InheritanceManager
from rdkit import Chem as chem
from rdkit.Chem import AllChem, rdFMCS
import os
import json
from collections import OrderedDict
from compounddb.models import Compound
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from  django.core.validators import validate_comma_separated_integer_list
class Cluster(models.Model):
    '''Cluster is defined by GenBank and MIBiG accession numbers.

    # Properties
        mibigAccession: str. MIBiG accession number.
        genbankAccession: str. GenBank accession number.
        description: str. known natural product of cluster.
        sequence: str. nucleotide sequence of cluster.
        knownProductSmiles: str. Known final product from literature or external databases, in smiles format.
        knownProductMCS: str. SMARTS string of MCS comparing knownProductSmiles to the predicted final product. Auto-generated when running self.computeProduct().
        knownProductSource: str. Where the knownProduct structure was obtained from.
        reviewed: bool. True if the final chemical structure has been manually reviewed for correctness. This is usually set to True only if a corrections file is provided.

    # Methods
        subunits: Returns subunits in cluster.
        architecture: Returns structure of cluster as list of lists.
        reorderSubunits: Reorders subunits in cluster.
        computeProduct: Compute list of intermediates for each module in cluster.
        setIterations: Sets module iterations parameter specificying number of iterations.
        setActive: Sets module KR, DH, ER, oMT, or cMT domain active boolean.
        setSubstrate: Sets AT substrate specificity of module.
        setStereochemistry: Sets KR stereochemistry of module.
        setCyclization: Sets cyclization of cluster TE.
        clusterDict: Generates OrderedDict representation of cluster.
        clusterJSON: Generates JSON file representation of cluster and save to file path.
        correctCluster: Corrects errors in cluster using JSON file.
                        Template JSON file should be generated using clusterJSON.
    '''
    mibigAccession = models.CharField(max_length=100, primary_key=True)
    genbankAccession = models.CharField(max_length=100)
    description = models.TextField()
    sequence = models.TextField()
    knownProductSmiles = models.TextField()
    knownProductMCS = models.TextField()
    knownProductSource = models.TextField(default='unknown')
    reviewed = models.BooleanField(default=False)

    def subunits(self):
        return Subunit.objects.filter(cluster=self).order_by('order')

    def architecture(self):
        # Returns the entire structure of the cluster
        return [[x, x.architecture()] for x in self.subunits()]

    def computeProduct(self, computeMCS=True, recompute=False):
        chain = []
        for subunit in self.subunits():
            for module in subunit.modules():
                if recompute:
                    module.deleteProduct()
                if len(chain) == 0:
                    chain.append(module.computeProduct())
                else:
                    chain.append(module.computeProduct(chain[-1]))

        if computeMCS:
                # MCS computation timeout adjusted 10 minutes to increase time for large clusters like gramicidin
                mcs = rdFMCS.FindMCS([chem.MolFromSmiles(self.knownProductSmiles), chain[-1]], timeout=600)
                self.knownProductMCS = mcs.smartsString
                self.save()
        return chain

    def reorderSubunits(self, newOrder):
        '''Takes as input a list of subunit names and reorders subunits within
           the gene cluster.
        '''
        for subunit in self.subunits():
            assert subunit.name in newOrder, 'Missing subunit %s.' %(subunit)
        subunits = [Subunit.objects.get(cluster__exact=self, name__exact=x) for x in newOrder]
        assert len(newOrder) == len(subunits), 'Non-existant subunits provided in new order.'

        # Reset loading bool of first module in oldOrder
        if len(self.subunits()[0].modules()) > 0:
            oldLoading = self.subunits()[0].modules()[0]
            oldLoading.loading = False
            oldLoading.setLoading()
            oldLoading.save()

        # Update subunit ordering
        subunitCounter = 0
        moduleCounter = 0
        for subunit in subunits:
            subunit.order = subunitCounter
            subunit.save()
            subunitCounter += 1

            # update module ordering
            modules = subunit.modules()
            for module in modules:
                module.order = moduleCounter
                module.deleteProduct()
                module.save()
                moduleCounter += 1

        # Reset loading bool of first module in newOrder
        newLoading = self.subunits()[0].modules()[0]
        newLoading.loading = True
        newLoading.setLoading()
        newLoading.save()

        return self.subunits()

    def setIterations(self, sub, mod, iterations):
        module = Module.objects.filter(subunit__cluster=self,
                                       subunit__name=sub).order_by('order')[mod]
        module.iterations = iterations
        module.save()

    def setActive(self, sub, mod, dom, active):
        assert dom in ['KR', 'DH', 'ER', 'oMT', 'cMT', 'Ox', 'Red', 'E', 'nMT', 'F', 'AOX', 'R', 'X']
        assert isinstance(active, bool)
        module = Module.objects.filter(subunit__cluster=self,
                                       subunit__name=sub).order_by('order')[mod]
        domains = Domain.objects.filter(module=module).select_subclasses()
        domain = list(filter(lambda x: repr(x) == dom, list(domains)))[0]
        domain.active = active
        domain.save()

    def setSubstrate(self, sub, mod, update):
        assert update in list(set(list(starters.keys()) + list(extenders.keys()))), update
        module = Module.objects.filter(subunit__cluster=self,
                                       subunit__name=sub).order_by('order')[mod]
        domains = {type(domain): domain for domain in module.domains()}

        # check that there is only one AT/A/CAL in the module
        num_at_cal_a = 0
        for domain in domains:
            if domain == AT or domain == CAL or domain == A:
                num_at_cal_a = num_at_cal_a + 1
        assert (num_at_cal_a == 1, "Less/more than one of the following domains found: AT/CAL/A")

        if AT in domains:
            domain = AT.objects.get(module=module)
        elif CAL in domains:
            domain = CAL.objects.get(module=module)
        elif A in domains:
            domain = A.objects.get(module=module)
        domain.substrate = update
        domain.save()
        
    def setStereochemistry(self, sub, mod, update):
        assert update in [x[0] for x in KR.TYPE_CHOICES]
        module = Module.objects.filter(subunit__cluster=self,
                                       subunit__name=sub).order_by('order')[mod]
        domain = KR.objects.get(module=module)
        domain.type = update
        domain.save()
    
    # sets R domain's chain termination type
    def setType(self, sub, mod, update):
        assert update in [x[0] for x in R.TYPE_CHOICES]
        module = Module.objects.filter(subunit__cluster=self,
                                       subunit__name=sub).order_by('order')[mod]
        domain = R.objects.get(module=module)
        domain.type = update
        domain.save()

    def setCyclization(self, cyclic, ring=0):
        assert isinstance(cyclic, bool)
        assert isinstance(ring, int)
        domain = TE.objects.get(module__subunit__cluster=self)
        domain.cyclic = cyclic
        if cyclic:
            domain.ring = ring
        domain.save()

    def clusterDict(self):
        '''Function that generates OrderedDict representation of changeable parameters
           describing a PKS cluster.
        '''
        ret = OrderedDict()
        ret.update({'description': self.description})
        ret.update({'genbankAccession': self.genbankAccession})
        ret.update({'mibigAccession': self.mibigAccession})
        adict = OrderedDict()
        for subunit in self.subunits():
            sname = subunit.name
            sdict = OrderedDict()
            for imodule,module in enumerate(subunit.modules()):
                mdict = OrderedDict()
                for domain in module.domains():
                    dname = repr(domain)
                    ddict = OrderedDict()
                    # PKS domains
                    if dname == 'AT':
                        ddict.update({'substrate': domain.substrate})
                    elif dname == 'CAL':
                        ddict.update({'substrate': domain.substrate})
                    elif dname == 'KR':
                        ddict.update({'active': domain.active,
                                      'type': domain.type})
                    elif dname in ['DH', 'ER', 'cMT', 'oMT']:
                        ddict.update({'active': domain.active})
                    elif dname == 'TE':
                        ddict.update({'cyclic': domain.cyclic,
                                      'ring': domain.ring})
                    # NRPS domains
                    elif dname == 'A':
                        ddict.update({'substrate': domain.substrate})
                    elif dname == 'R':
                        ddict.update({'active': domain.active, 
                                      'type': domain.type})
                    elif dname in ['Ox', 'Red', 'E', 'nMT', 'F', 'AOX', 'X']:
                        ddict.update({'active': domain.active})

                    if dname in ['AT', 'CAL', 'KR', 'DH', 'ER', 'cMT', 'oMT', 'TE', 'A', 'Cy', 'Ox', 'Red', 'E', 'nMT', 'F', 'AOX', 'R', 'X']:
                        mdict.update({dname: ddict})
                sdict.update({imodule: {'domains': mdict,
                                        'iterations': module.iterations}})
            adict.update({sname: sdict})
        ret.update({'architecture': adict})
        return ret

    def clusterJSON(self, path):
        '''Function that writes a JSON file containing the changeable parameters
            describing a PKS cluster.
        '''
        with open(os.path.join(path, self.mibigAccession + '.json'), 'w') as f:
            f.write(json.dumps(self.clusterDict(), indent=4))

    def correctCluster(self, filepath):
        '''Function that takes as input a JSON file representing the changeable parameters
           describing a PKS cluster and updates the database entry to reflect the information
           contained in the JSON file.
        '''
        corr = json.loads(open(filepath).read(), object_pairs_hook=OrderedDict)
        assert corr['mibigAccession'] == self.mibigAccession
        assert corr['genbankAccession'] == self.genbankAccession
        
        # correct name if necessary
        if self.description != corr['description']:
            self.description = corr['description']

        # Delete subunits if necessary
        for s in Subunit.objects.filter(cluster=self):
            if s.name not in corr['architecture'].keys():
                Subunit.objects.get(cluster=self, name=s).delete()
        # Change domain properties if necessary
        for s,sdict in corr['architecture'].items():
            for m,mdict_iters in sdict.items():
                m = int(m) # Key is expected to be integer
                mdict = mdict_iters['domains']
                iters = mdict_iters['iterations']
                self.setIterations(s, m, iters)
                for d,ddict in mdict.items():
                    # PKS domains
                    if d == 'AT':
                        self.setSubstrate(s, m, ddict['substrate'])
                    elif d == 'CAL':
                        self.setSubstrate(s, m, ddict['substrate'])
                    elif d == 'KR':
                        self.setStereochemistry(s, m, ddict['type'])
                        self.setActive(s, m, d, ddict['active'])
                    elif d in ['DH', 'ER', 'cMT', 'oMT']:
                        self.setActive(s, m, d, ddict['active'])
                    # NRPS domains
                    elif d == 'A':
                        self.setSubstrate(s, m, ddict['substrate'])
                    elif d == 'Cy':
                        continue
                    elif d == 'R':
                        self.setType(s,m, ddict['type'])
                        self.setActive(s, m, d, ddict['active'])
                    elif d in ['Ox', 'Red', 'E', 'nMT', 'F', 'AOX', 'X']:
                        self.setActive(s, m, d, ddict['active'])
                    else:
                        assert d == 'TE'
                        cyclic = ddict['cyclic']
                        ring = int(ddict['ring'])
                        self.setCyclization(cyclic, ring)
        # Reorder subunits if necessary
        # Must be done last since this is when products are recomputed
        newOrder = [str(x) for x in corr['architecture'].keys()]
        self.reorderSubunits(newOrder)
        self.computeProduct(recompute=True)

    def __str__(self):
        return "%s gene cluster" % self.description

class Subunit(models.Model):
    ''' Class representing a PKS subunit.

    # Properties
        cluster: class<Cluster>. cluster containing subunit.
        order: int. order of subunit within cluster starting with 0. Auto-set on self.save()
        genbankAccession: str. GenBank accession number.
        name: str. name of subunit.
        start: int. start of subunit in cluster nucleotide sequence.
        stop: int. end of subunit in cluster nucleotide sequence.
        sequence: str. amino acid sequence corresponding to subunit.

    # Methods
        modules: Returns modules in subunit.
        domains: Returns domains in subunit.
        architecture: Returns architecture of subunit.
        getNucleotideSequence: Returns nucleotide sequence of subunit.
        getAminoAcidSequence: Returns amino acid sequence of subunit.
    '''
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    order = models.IntegerField()
    genbankAccession = models.CharField(max_length=2000, unique=False)
    name = models.CharField(max_length=2000)
    start = models.PositiveIntegerField()
    stop = models.PositiveIntegerField()
    sequence = models.TextField()
    acc = models.TextField()
    acc20 = models.CharField(validators = [validate_comma_separated_integer_list], max_length=1000000)
    accPlotFile = models.ImageField(upload_to='accplots')
    ss = models.TextField()
    ss8 = models.TextField()
    ssPlotFile = models.ImageField(upload_to='ssplots')

    # determines if subunit is on complement strand (-)/is not (+)
    # useful for subunit reordering within cluster
    sense = models.CharField(max_length=3)

    def modules(self):
        return Module.objects.filter(subunit=self).order_by('order')

    def architecture(self):
        return [[x, x.domains()] for x in self.modules()]

    def getNucleotideSequence(self):
        return self.cluster.sequence[(self.start - 1):self.stop]

    def getAminoAcidSequence(self):
        return self.sequence

    def __str__(self):
        return "%s" % self.name

@receiver(pre_save, sender=Subunit)
def setSubunitOrder(sender, instance, **kwargs):
    # sets the subunit order
    if not isinstance(instance.order, int):
        subunitCount = sender.objects.filter(cluster=instance.cluster).count()
        instance.order = subunitCount

class Module(models.Model):
    '''Class representing a PKS module.

    # Properties
        subunit: class<Subunit>. subunit containing module.
        order: int. order of module within cluster starting with 0. Auto-set on self.save()
        loading: bool. Whether or not module is a loading module.
        terminal: bool. Whether or not module is a terminal module.
        product: class<Compound>. Product small molecule structure.

    # Methods
        domains: Returns domains in subunit.
        setLoading: Resets activity of reductive casette based on whether module is loading.
        buildDomains: Build class<Domain> objects using dict as input
        computeProduct: Compute product of module given chain.
        deleteProduct: Reset product to Null, and properly delete it from database.
    '''
    subunit = models.ForeignKey(Subunit, on_delete=models.CASCADE)
    order = models.IntegerField()
    loading = models.BooleanField() # Whether or not module is a loading module
    terminal = models.BooleanField() # Whether or not module is a terminal module
    product = models.ForeignKey(Compound, on_delete=models.SET_NULL, default=None, blank=True, null=True) # small molecule product structure
    iterations = models.PositiveIntegerField(default=1)

    def domains(self):
        return Domain.objects.filter(module=self).select_subclasses().order_by('start')

    def setLoading(self):
        domains = Domain.objects.filter(module=self).select_subclasses(KR, DH, ER, cMT, oMT)
        if self.loading:
            for d in domains:
                d.active = False
                d.save()
        else:
            for d in domains:
                d.active=True
                d.save()

    def buildDomains(self, domainDict, cyclic=False):
        if 'CAL' in domainDict.keys():
            start = domainDict['CAL'][0]['start']
            stop = domainDict['CAL'][0]['stop']
            substrate = domainDict['CAL'][1]['Substrate specificity predictions'].split()[0]
            if substrate == 'N/A':
                substrate = domainDict['CAL'][1]['Substrate specificity predictions'].split()[3]
            if substrate == 'N/A':
                substrate = 'mal'
            newDomain = CAL(module=self, start=start, stop=stop, substrate=substrate)
            newDomain.save()

        if 'AT' in domainDict.keys():
            start = domainDict['AT'][0]['start']
            stop = domainDict['AT'][0]['stop']
            substrate = domainDict['AT'][1]['Substrate specificity predictions'].split()[0]
            if substrate == 'N/A':
                substrate = domainDict['AT'][1]['Substrate specificity predictions'].split()[3]
            if substrate == 'N/A':
                substrate = 'mal'
            newDomain = AT(module=self, start=start, stop=stop, substrate=substrate)
            newDomain.save()

        if 'KR' in domainDict.keys():
            start = domainDict['KR'][0]['start']
            stop = domainDict['KR'][0]['stop']
            type =  domainDict['KR'][1]['Predicted KR stereochemistry']
            if type == '?':
                type = 'U'
            activity = domainDict['KR'][1]['Predicted KR activity']
            if activity == 'active':
                active = True
            else:
                active = False
            newDomain = KR(module=self, start=start, stop=stop, active=active, type=type)
            newDomain.save()

        #A domain for NRPS
        if 'A' in domainDict.keys():
            start = domainDict['A'][0]['start']
            stop = domainDict['A'][0]['stop']
            substrate = domainDict['A'][1]['Substrate specificity predictions'].split()[0]
            if "," in substrate:
                substrate = domainDict['A'][1]['Substrate specificity predictions'].split()[0].split(',')[0]

            # if substrate is invalid or not implemented, check second substrate entry
            if (substrate not in starters) or (substrate not in extenders):
                print("Substrate not recognized, checking next one. ")
                substrate = domainDict['A'][1]['Substrate specificity predictions'].split()[3]
            
            if substrate == 'N/A':
                substrate = domainDict['A'][1]['Substrate specificity predictions'].split()[3]
            if substrate == 'N/A':
                substrate = 'gly'
            print("A domain info: ")
            print(domainDict['A'])
            newDomain = A(module=self, start=start, stop=stop, substrate=substrate)
            newDomain.save()
        
        # 4 different C domain subtypes
        if 'Condensation' in domainDict.keys():
            start = domainDict['Condensation'][0]['start']
            stop = domainDict['Condensation'][0]['stop']
            type = 'Unknown'
            newDomain = C(module=self, start=start, stop=stop, type=type)
            newDomain.save()

        if 'Condensation_Starter' in domainDict.keys():
            start = domainDict['Condensation_Starter'][0]['start']
            stop = domainDict['Condensation_Starter'][0]['stop']
            type = 'Starter'
            newDomain = C(module=self, start=start, stop=stop, type=type)
            newDomain.save()

        if 'Condensation_LCL' in domainDict.keys():
            start = domainDict['Condensation_LCL'][0]['start']
            stop = domainDict['Condensation_LCL'][0]['stop']
            type = 'LCL'
            newDomain = C(module=self, start=start, stop=stop, type=type)
            newDomain.save()

        if 'Condensation_DCL' in domainDict.keys():
            start = domainDict['Condensation_DCL'][0]['start']
            stop = domainDict['Condensation_DCL'][0]['stop']
            type = 'DCL'
            newDomain = C(module=self, start=start, stop=stop, type=type)
            newDomain.save()
        
        if 'Cy' in domainDict.keys():
            start = domainDict['Cy'][0]['start']
            stop = domainDict['Cy'][0]['stop']
            newDomain = Cy(module=self, start=start, stop=stop)
            newDomain.save()

        if 'E' in domainDict.keys():
            start = domainDict['E'][0]['start']
            stop = domainDict['E'][0]['stop']
            newDomain = E(module=self, start=start, stop=stop)
            newDomain.save()

        # PKS and NRPS domains
        for domainType in ['KS', 'DH', 'ER', 'cMT', 'oMT', 'ACP', 'PCP', 'Ox', 'Red', 'nMT', 'F', 'X']: 
            if domainType in domainDict.keys():
                start = domainDict[domainType][0]['start']
                stop = domainDict[domainType][0]['stop']
                if domainType in ['DH', 'ER', 'cMT', 'oMT', 'Ox', 'Red', 'nMT', 'F', 'AOX', 'X']:
                    newDomain = getattr(sys.modules[__name__], domainType)(module=self, start=start, stop=stop, active=True)
                else:
                    newDomain = getattr(sys.modules[__name__], domainType)(module=self, start=start, stop=stop)
                newDomain.save()
        
        if 'AOX' in domainDict.keys():
            start = domainDict['AOX'][0]['start']
            stop = domainDict['AOX'][0]['stop']
            newDomain = AOX(module=self, start=start, stop=stop)
            newDomain.save()
        
        if 'R' in domainDict.keys():
            start = domainDict['R'][0]['start']
            stop = domainDict['R'][0]['stop']
            type =  'alcohol'
            active = True
            newDomain = R(module=self, start=start, stop=stop, active=active, type=type)
            newDomain.save()

        if 'Thioesterase' in domainDict.keys():
            start = domainDict['Thioesterase'][0]['start']
            stop = domainDict['Thioesterase'][0]['stop']
            newDomain = TE(module=self, start=start, stop=stop, cyclic=cyclic, ring=0)
            newDomain.save()

        self.setLoading()

    def computeProduct(self, chain=False):
        if self.product:
            return self.product.mol()
        domains = {type(domain): domain for domain in self.domains()}
        reactionOrder = [CAL, AT, A, F, Cy, Ox, Red, E, nMT, KR, cMT, oMT, DH, ER, X, AOX, R, TE]
        for iteration in range(self.iterations):
            for reaction in reactionOrder:
                
                if reaction in domains.keys():

                    # if R or AOX (alt chain release domains) is present in the same module as TE, skip TE
                    # reaction order guarentees TE will be after AOX or R
                    if ((reaction == TE) and (AOX in domains.keys())) or ((reaction == TE) and (R in domains.keys())):
                        continue
                    else:
                        chain = domains[reaction].operation(chain)

        # Save this modules product in the database
        thisProduct = Compound(smiles = chem.MolToSmiles(chain, isomericSmiles=True))
        thisProduct.save()
        self.product = thisProduct
        self.save()
        return chain

    def deleteProduct(self):
        # set self.product to none, and delete the compound itself
        # if this is the only module
        if Module.objects.filter(product=self.product).exclude(id=self.id).count() == 0 and self.product != None:
            self.product.delete()
        self.product = None

    def loadingStr(self):
        if self.loading:
            return 'loading'
        else:
            return 'non-loading'

    def __str__(self):
        return "%s" % str(self.order)

@receiver(pre_delete, sender=Module)
def deleteModuleProduct(sender, instance, **kwargs):
    instance.deleteProduct()

@receiver(pre_save, sender=Module)
def setModuleOrder(sender, instance, **kwargs):
    # sets the module order based on current count
    if not isinstance(instance.order, int):
        moduleCount = sender.objects.filter(subunit__cluster=instance.subunit.cluster).count()
        instance.order = moduleCount

class Domain(models.Model):
    ''' Abstract base class used to build PKS catalytic domains.

    # Properties
        module: class<Module>. module containing domain.
        start: int. start of domain in subunit amino acid sequence.
        stop: int. end of domain in subunit amino acid sequence.

    # Methods
        getNucleotideSequence: Returns nucleotide sequence of domain.
        getAminoAcidSequence: Returns amino acid sequence of domain.
    '''
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    start = models.PositiveIntegerField()
    stop = models.PositiveIntegerField()

    # Using InheritanceManager allows us to directly
    # query all Domain subclasses
    objects = InheritanceManager()

    def getAminoAcidSequence(self):
        sequence = self.module.subunit.getAminoAcidSequence()
        return sequence[(self.start - 1):self.stop]

def activityString(domain):
    if domain.active:
        return 'active'
    else:
        return 'inactive'

# dict of supported starter and extender units
# merged with NRPS substrates after the nrps_substrates dictionary

pks_starters = {'mal': chem.MolFromSmiles('CC(=O)[S]'),
            'mmal': chem.MolFromSmiles('CCC(=O)[S]'),
            'butmal': chem.MolFromSmiles('CCCC(=O)[S]'),
            'mxmal': chem.MolFromSmiles('COCC(=O)[S]'),
            'mxmal_ACP': chem.MolFromSmiles('COCC(=O)[S]'),
            'cemal': chem.MolFromSmiles('CC(=O)[S]'),
            'Acetyl-CoA': chem.MolFromSmiles('CC(=O)[S]'),
            'prop': chem.MolFromSmiles('CCC(=O)[S]'),
            'isobut': chem.MolFromSmiles('CC(C)C(=O)[S]'),
            '2metbut': chem.MolFromSmiles('CCC(C)C(=O)[S]'),
            'CHC-CoA': chem.MolFromSmiles('C1CCCCC1C(=O)[S]'),
            'trans-1,2-CPDA': chem.MolFromSmiles('C1CC[C@@H](C(=O)O)[C@@H]1C(=O)[S]'),
            'cyclopentene': chem.MolFromSmiles('C1(=O)C(=CCC1)C(=O)[S]'),
            'pyr': chem.MolFromSmiles('[S]C(C1=CC=CN1)=O'),
            'cin': chem.MolFromSmiles('O=C([S])/C=C/C1=CC=CC=C1'),
            'AHBA': chem.MolFromSmiles('[S]C(C1=CC(O)=CC(N)=C1)=O'),
            'isoval': chem.MolFromSmiles('CC(CC([S])=O)C'),
            'PABA': chem.MolFromSmiles('NC1=CC=C(C([S])=O)C=C1'),
            'DCP': chem.MolFromSmiles('[S]C(C1=CNC(Cl)=C1Cl)=O'),
            'guan': chem.MolFromSmiles('NC(NCC([S])=O)=[NH2+]'),
            'mthz': chem.MolFromSmiles('CC1=NC(C([S])=O)=CS1'),
            'DHCH': chem.MolFromSmiles('O[C@H]1[C@H](O)CCC(C([S])=O)C1'),
            'DHCHene': chem.MolFromSmiles('O[C@H]1[C@H](O)CC=C(C([S])=O)C1'),
            'plac': chem.MolFromSmiles('O=C([S])CC1=CC=CC=C1'),
            'benz': chem.MolFromSmiles('[S]C(C1=CC=CC=C1)=O'),
            'PNBA': chem.MolFromSmiles('[S]C(C1=CC=C([N+]([O-])=O)C=C1)=O'),
            'ema': chem.MolFromSmiles('[S]C([C@@H](CC)C(N)=O)=O'),
            '3measp': chem.MolFromSmiles('[S]C([C@@H](C)CNC([C@@H](N)C)=O)=O'),
            # the following structures still need confirmation
            'AAnon': chem.MolFromSmiles('[S]C(CC(NC([C@H](C)N)=O)CCCCCC)=O'),
            'a3abut': chem.MolFromSmiles('[S]C(C[C@@H](NC(C)=O)C)=O'),
            'shikimic_acid': chem.MolFromSmiles('C1[C@H]([C@@H]([C@@H](C=C1C(=O)[S])O)O)O'),
            'fatty_acid': chem.MolFromSmiles('CCCC(=O)[S]'),
            'NH2': chem.MolFromSmiles('NCC(=O)[S]'),
            'N/A': None,
           }

pks_extenders = {'mal': chem.MolFromSmiles('O=C(O)CC(=O)[S]'),
             'mmal': chem.MolFromSmiles('C[C@@H](C(=O)O)C(=O)[S]'),
             'mxmal': chem.MolFromSmiles('CO[C@@H](C(=O)O)C(=O)[S]'),
             'mxmal_ACP': chem.MolFromSmiles('CO[C@@H](C(=O)O)C(=O)[S]'),
             'emal': chem.MolFromSmiles('CC[C@@H](C(=O)O)C(=O)[S]'),
             'allylmal': chem.MolFromSmiles('C=CC[C@@H](C(=O)O)C(=O)[S]'),
             'butmal': chem.MolFromSmiles('CCCC[C@@H](C(=O)O)C(=O)[S]'),
             'hmal': chem.MolFromSmiles('OC(C(C([S])=O)O)=O'),
             'isobutmal': chem.MolFromSmiles('CC(C)[C@@H](C([S])=O)C(O)=O'),
             'D-isobutmal': chem.MolFromSmiles('CC(C)[C@H](C([S])=O)C(O)=O'),
             'DCP': chem.MolFromSmiles('ClC1=C(Cl)NC=C1CCCCC(C(O)=O)C([S])=O'),
             'hexmal': chem.MolFromSmiles('CCCCCC[C@@H](C(=O)O)C(=O)[S]'),
             }

nrps_substrates = {
    # L-amino acids - use format <R_group>C[C@H](N)C(=O)[S] for L stereochemistry
    
    # special
    'gly': chem.MolFromSmiles('NCC(=O)[S]'),
    'cys': chem.MolFromSmiles('SC[C@H](N)C(=O)[S]'),
    'pro': chem.MolFromSmiles('C1CC[C@H](N1)C(=O)[S]'),
    
    # polar uncharged
    'ser': chem.MolFromSmiles('OC[C@H](N)C(=O)[S]'),
    'thr': chem.MolFromSmiles('CC(O)[C@H](N)C(=O)[S]'),
    'asn': chem.MolFromSmiles('NC(=O)C[C@H](N)C(=O)[S]'),
    'gln': chem.MolFromSmiles('NC(=O)CC[C@H](N)C(=O)[S]'),
    
    # polar charged
    'arg': chem.MolFromSmiles('N=C(N)NCCC[C@H](N)C(=O)[S]'),
    'his': chem.MolFromSmiles('N1=CNC=C1C[C@H](N)C(=O)[S]'),
    'lys': chem.MolFromSmiles('NCCCC[C@H](N)C(=O)[S]'),
    'asp': chem.MolFromSmiles('OC(=O)C[C@H](N)C(=O)[S]'),
    'glu': chem.MolFromSmiles('OC(=O)CC[C@H](N)C(=O)[S]'),
    
    # nonpolar
    'ala': chem.MolFromSmiles('C[C@H](N)C(=O)[S]'),
    'val': chem.MolFromSmiles('CC(C)[C@H](N)C(=O)[S]'),
    'ile': chem.MolFromSmiles('CCC(C)[C@H](N)C(=O)[S]'),
    'leu': chem.MolFromSmiles('CC(C)C[C@H](N)C(=O)[S]'),
    'met': chem.MolFromSmiles('CSCC[C@H](N)C(=O)[S]'),
    'phe': chem.MolFromSmiles('C1=CC=CC=C1C[C@H](N)C(=O)[S]'),
    'tyr': chem.MolFromSmiles('C1=CC(O)=CC=C1C[C@H](N)C(=O)[S]'),
    'trp': chem.MolFromSmiles('C2=CC=CC1=C2C(=CN1)C[C@H](N)C(=O)[S]'), 
    
    # amino acid derivatives
    'pip': chem.MolFromSmiles('C1CC[N]C(C1)C(=O)[S]'),
    'd-ala': chem.MolFromSmiles('C[C@@H](N)C(=O)[S]'),
    'bmt': chem.MolFromSmiles('C/C=C/C[C@@H](C)[C@@H](O)C(N)C(=O)[S]'),
    'aba': chem.MolFromSmiles('CC[C@H](N)C(=O)[S]'),
    'orn': chem.MolFromSmiles('NCCC[C@H](N)C(=O)[S]'), # ornithine
    'htyr': chem.MolFromSmiles("C1=CC(=CC=C1CC[C@@H](C(=O)[S])N)O"), # homotyrosine
    'hpla' : chem.MolFromSmiles("C1=CC(=CC=C1C[C@H](C(=O)[S])O)O"), # 2R-hydroxyphenyl lactic acid
    'mpro': chem.MolFromSmiles('C[C@H]1C[C@H](NC1)C(=O)[S]'),
    '3cl-tyr': chem.MolFromSmiles('C1=C(Cl)C(O)=CC=C1C[C@H](N)C(=O)[S]'), #3-chlorotyrosine

}

# update starters and extenders list with NRPS substrates
starters = {**pks_starters, **nrps_substrates}
extenders = {**pks_extenders, **nrps_substrates}


class CAL(Domain):
    SUBSTRATE_CHOICES = tuple(((k, k) for k in list(set(list(extenders.keys()) + list(starters.keys())))))

    substrate = models.CharField(
        max_length=20,
        choices=SUBSTRATE_CHOICES,
        default='mal',
        blank=False,
    )

    def operation(self, chain):
        assert self.module.loading == True
        return starters[self.substrate]

    def __str__(self):
        if self.module.iterations > 1:
            return "substrate %s, %s, iterations %d" % (self.substrate, self.module.loadingStr(), self.module.iterations)
        else:
            return "substrate %s, %s" % (self.substrate, self.module.loadingStr())

    def __repr__(self):
        return("CAL")

class AT(Domain):
    SUBSTRATE_CHOICES = tuple(((k, k) for k in list(set(list(extenders.keys()) + list(starters.keys())))))

    substrate = models.CharField(
        max_length=20,
        choices=SUBSTRATE_CHOICES,
        default='mal',
        blank=False,
    )

    def operation(self, chain):
        if not chain:
            return starters[self.substrate]
        else:
            rxn = AllChem.ReactionFromSmarts(('[C:2](=[O:3])[S].'
                                              '[O:4][C:5](=[O:6])[C@@:7][C:8](=[O:9])[S:10]>>'
                                              '[C:2](=[O:3])[C@:7][C:8](=[O:9])[S:10]'
                                              '.[C:5](=[O:4])(=[O:6])'))
            assert KS in [type(domain) for domain in self.module.domains()]
            assert len(chain.GetSubstructMatches(chem.MolFromSmiles('CC(=O)S'),
                       useChirality=True)) == 1, chem.MolToSmiles(chain)
            prod = rxn.RunReactants((chain, extenders[self.substrate]))[0][0]
            chem.SanitizeMol(prod)
            return prod

    def __str__(self):
        if self.module.iterations > 1:
            return "substrate %s, %s, iterations %d" % (self.substrate, self.module.loadingStr(), self.module.iterations)
        else:
            return "substrate %s, %s" % (self.substrate, self.module.loadingStr())

    def __repr__(self):
        return("AT")

class KR(Domain):
    active = models.BooleanField()
    TYPE_CHOICES = (
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('A', 'A'),
        ('B1', 'B1'),
        ('B2', 'B2'),
        ('B', 'B'),
        ('C1', 'C1'),
        ('C2', 'C2'),
        ('U', 'U'),
    )
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default=None,
        blank=False,
    )

    def operation(self, chain):
        # Reaction is fixed once KR type is assigned
        if self.type == 'A1':
            rxn = AllChem.ReactionFromSmarts(('[C:2](=[O:3])[C:4]'
                                                   '[C:5](=[O:6])[S:7]>>'
                                                   '[C@:2]([O:3])[C@:4]'
                                                   '[C:5](=[O:6])[S:7]'))
        elif self.type == 'A2':
            rxn = AllChem.ReactionFromSmarts(('[C:2](=[O:3])[C:4]'
                                                   '[C:5](=[O:6])[S:7]>>'
                                                   '[C@:2]([O:3])[C@@:4]'
                                                   '[C:5](=[O:6])[S:7]'))
        elif self.type == 'A':
            rxn = AllChem.ReactionFromSmarts(('[C:2](=[O:3])[C:4]'
                                                   '[C:5](=[O:6])[S:7]>>'
                                                   '[C@:2]([O:3])[C:4]'
                                                   '[C:5](=[O:6])[S:7]'))
        elif self.type == 'B1':
            rxn = AllChem.ReactionFromSmarts(('[C:2](=[O:3])[C:4]'
                                                   '[C:5](=[O:6])[S:7]>>'
                                                   '[C@@:2]([O:3])[C@:4]'
                                                   '[C:5](=[O:6])[S:7]'))
        elif self.type == 'B2':
            rxn = AllChem.ReactionFromSmarts(('[C:2](=[O:3])[C:4]'
                                                   '[C:5](=[O:6])[S:7]>>'
                                                   '[C@@:2]([O:3])[C@@:4]'
                                                   '[C:5](=[O:6])[S:7]'))
        elif self.type == 'B':
            rxn = AllChem.ReactionFromSmarts(('[C:2](=[O:3])[C:4]'
                                                   '[C:5](=[O:6])[S:7]>>'
                                                   '[C@@:2]([O:3])[C:4]'
                                                   '[C:5](=[O:6])[S:7]'))
        elif self.type == 'C1':
            rxn = AllChem.ReactionFromSmarts(('[C:2](=[O:3])[C:4]'
                                                   '[C:5](=[O:6])[S:7]>>'
                                                   '[C:2](=[O:3])[C:4]'
                                                   '[C:5](=[O:6])[S:7]'))
        elif self.type == 'C2':
            rxn = AllChem.ReactionFromSmarts(('[C:2](=[O:3])[C:4]'
                                                   '[C:5](=[O:6])[S:7]>>'
                                                   '[C:2](=[O:3])[C@@:4]'
                                                   '[C:5](=[O:6])[S:7]'))
        else:
            # By first specifying some stereochemistry in the reactants
            # and then explicitly "losing" the stereochemistry in the products
            # we can forget the stereochemistry in our molecule
            rxn = AllChem.ReactionFromSmarts(('[C:2](=[O:3])[C@:4]'
                                                   '[C:5](=[O:6])[S:7]>>'
                                                   '[C:2]([O:3])[C:4]'
                                                   '[C:5](=[O:6])[S:7]'))
        if self.active == True:
            assert len(chain.GetSubstructMatches(chem.MolFromSmiles('C(=O)CC(=O)S'),
                       useChirality=True)) == 1, chem.MolToSmiles(chain)
            prod = rxn.RunReactants((chain,))[0][0]
            chem.SanitizeMol(prod)
        else:
            prod = chain
        return prod

    def __str__(self):
        return "type %s, %s" % (self.type, activityString(self))

    def __repr__(self):
        return("KR")

class DH(Domain):
    active = models.BooleanField(default=True)

    def operation(self, chain):
        rxn = AllChem.ReactionFromSmarts(('[C:2]([O:3])[C:4][C:6](=[O:7])[S:8]>>'
                                          '[CH1:2]=[CH0:4][C:6](=[O:7])[S:8].[O:3]'))
        # Changed assertion to if/else statement so that DH and ER do not
        # do anything if the KR is inactive
        if len(chain.GetSubstructMatches(chem.MolFromSmiles('C(O)CC(=O)S'), useChirality=True)) == 1 and self.active == True:
            prod = rxn.RunReactants((chain,))[0][0]
            chem.SanitizeMol(prod)
            return prod
        else:
            return chain

    def __str__(self):
        return activityString(self)

    def __repr__(self):
        return("DH")

class ER(Domain):
    active = models.BooleanField(default=True)

    def operation(self, chain):
        rxn = AllChem.ReactionFromSmarts(('[C:2]=[C:3][C:4](=[O:5])[S:6]>>'
                                          '[C:2][C@@H1:3][C:4](=[O:5])[S:6]'))
        if len(chain.GetSubstructMatches(chem.MolFromSmiles('C=CC(=O)S'), useChirality=True)) == 1 and self.active == True:
            prod = rxn.RunReactants((chain,))[0][0]
            chem.SanitizeMol(prod)
            return prod
        else:
            return chain

    def __str__(self):
        return activityString(self)

    def __repr__(self):
        return("ER")

class cMT(Domain):
    active = models.BooleanField(default=True)

    def operation(self, chain):
        rxn = AllChem.ReactionFromSmarts(('[C:1][C:2](=[O:3])[S:4]>>'
                                          '[C:1](C)[C:2](=[O:3])[S:4]'))
        assert len(chain.GetSubstructMatches(chem.MolFromSmiles('CC(=O)S'),
                   )) == 1, chem.MolToSmiles(chain)
        if self.active == True:
            prod = rxn.RunReactants((chain,))[0][0]
            chem.SanitizeMol(prod)
            return prod
        else:
            return chain

    def __str__(self):
        return activityString(self)

    def __repr__(self):
        return("cMT")

class oMT(Domain):
    active = models.BooleanField(default=True)

    def operation(self, chain):
        if self.active == True:
            if len(chain.GetSubstructMatches(chem.MolFromSmiles('CC(=O)CC(=O)S'))) == 1:
                rxn = AllChem.ReactionFromSmarts(('[C:2](=[O:3])[C:4][C:5](=[O:6])[S:7]>>'
                                                  '[C:2]([O:3]C)[C:4][C:5](=[O:6])[S:7]'))
                prod = rxn.RunReactants((chain,))[0][0]
            elif len(chain.GetSubstructMatches(chem.MolFromSmiles('CC(O)CC(=O)S'))) == 1:
                rxn = AllChem.ReactionFromSmarts(('[C:2]([O:3])[C:4][C:5](=[O:6])[S:7]>>'
                                                  '[C:2]([O:3]C)[C:4][C:5](=[O:6])[S:7]'))
                prod = rxn.RunReactants((chain,))[0][0]
            else:
                prod = chain
            chem.SanitizeMol(prod)
            return prod
        else:
            return chain

    def __str__(self):
        return activityString(self)

    def __repr__(self):
        return("oMT")

class TE(Domain):
    cyclic = models.BooleanField()
    ring = models.IntegerField(default=0)

    def operation(self, chain):
        assert len(chain.GetSubstructMatches(chem.MolFromSmiles('C(=O)S'),
                   useChirality=True)) == 1, chem.MolToSmiles(chain)

        index = -1
        if self.cyclic:
            rxn = AllChem.ReactionFromSmarts('([C:1](=[O:2])[S:3].[O:4][C,c:5][C,c:6])>>'
                                                  '[C:1](=[O:2])[O:4][C,c:5][C,c:6].[S:3]')
            index -= self.ring
        else:
            rxn = AllChem.ReactionFromSmarts('[C:1](=[O:2])[S:3]>>[C:1](=[O:2])[O].[S:3]')

        # Using index -1 will yield the largest ring
        prod = rxn.RunReactants((chain,))[index][0]
        chem.SanitizeMol(prod)

        return prod

    def __str__(self):
        if self.cyclic:
            return 'cyclic'
        else:
            return 'non-cyclic'

    def __repr__(self):
        return("TE")

class KS(Domain):

    def __str__(self):
        return "domain"

    def __repr__(self):
        return("KS")

class ACP(Domain):

    def __str__(self):
        return "domain"

    def __repr__(self):
        return("ACP")



class Standalone(models.Model):
    # a standalone PKS enzyme within a gene cluster
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=2000) # name of enzyme
    start = models.PositiveIntegerField()
    stop = models.PositiveIntegerField()
    sequence = models.TextField()



# Beginning of NRPS support

# For the NRPS substrate list, go to nrps_substrates right before the PKS domain classes begin. 

class A(Domain):
    # Adenylation domain: picks substrate and catalyzes its addition to PCP

    SUBSTRATE_CHOICES = tuple(((k, k) for k in list(set(list(extenders.keys()) + list(starters.keys())))))

    substrate = models.CharField(
        max_length=25,
        choices=SUBSTRATE_CHOICES,
        default='gly', # simplest amino acid
        blank=False,
    )
    
    def operation(self, chain):
        
        if not chain:
            return nrps_substrates[self.substrate] # no chain = pass on the substrate
        else:
            rxn = AllChem.ReactionFromSmarts(('[C:2](=[O:3])[S:1].' # incoming chain
                                              '[N:6][C:7][C:8](=[O:9])[S:10]>>' # substrate
                                              '[C:2](=[O:3])[N:6][C:7][C:8](=[O:9])[S:10]' # product
                                              '.[S:1]')) # remaining thiol
            
            # ensure there is only one thiol ester (reaction site) in the chain
            assert len(chain.GetSubstructMatches(chem.MolFromSmiles('CC(=O)S'),
                       useChirality=True)) == 1, chem.MolToSmiles(chain)
            prod = rxn.RunReactants((chain, nrps_substrates[self.substrate]))[0][0]
            chem.SanitizeMol(prod)
            return prod

    def __str__(self):
        return 'substrate %s' % (self.substrate)

    def __repr__(self):
        return ("A")

class Cy(Domain):
    # (Hetero)Cyclization domain: picks substrate and cyclizes it, forming thiazoline or oxazoline
    # Does not pick substrate within clusterCAD, only cyclizes
    # Cyclizes cysteine/serine/threonine and requires a chain

    def operation(self, chain):
        
        # ensures that a chain preceeds cyclization domain
        assert chain
        
        # Intramolecular cyclization
        rxn = AllChem.ReactionFromSmarts(('[C,c:11]C(=[O:3])[N:6][C:7]([C:5][S,O:12])[C:8](=[O:9])[S:10]>>' # condensation product backbone
                                           '[C,c:11]C1=[N:6][C:7]([C:5][S,O:12]1)[C:8](=[O:9])[S:10]' # zoline moiety
                                           '.[O:3]')) # water from dehydration

        # make sure there is only one thiol ester-linked cyclization backbone
        assert len(chain.GetSubstructMatches(chem.MolFromSmarts('C(=O)NC(C[S,O])C(=O)S'),
               useChirality=True)) == 1, chem.MolToSmiles(chain)
        prod = rxn.RunReactants((chain,))[0][0] # intramolecular rxn
        chem.SanitizeMol(prod)
        return prod

    def __str__(self):
        return 'heterocyclization: constitutively active'

    def __repr__(self):
        return ("Cy")

class Ox(Domain):
    # Oxidation domain: Oxidizes any "zoline" moiety (thiazolines and oxazolines into thiazoles and oxazoles)
    # the operation function assumes Ox immediately follows Cy domain

    active = models.BooleanField(default=True)
    
    def operation(self, chain):
        
        if self.active == True:
            # make sure "zoline"-thioester moiety is present
            assert len(chain.GetSubstructMatches(chem.MolFromSmarts('C1=NC(C*1)C(=O)S'), useChirality=True)) == 1
            
            # attempts to oxidize ANY zoline moiety based on SMARTS
            rxn = AllChem.ReactionFromSmarts(('[C,c:11]C1=[N:6][CH1:7]([C:5][*:12]1)[C:8](=[O:9])[S:10]>>'
                                                  '[C,c:11]C1=[N:6][CH0:7](=[C:5][*:12]1)[C:8](=[O:9])[S:10]'))
            prod = rxn.RunReactants((chain,))[0][0]
            chem.SanitizeMol(prod)
            return prod
        
        else:
            return chain
    
    def __str__(self):
        return activityString(self)

    def __repr__(self):
        return ("Ox")

class Red(Domain):
    # Reduction domain: Reduces thiazolines and oxazolines into thiazolidines and oxazolidines
    # the operation function assumes Red immediately follows Cy domain
    # **NOT TO BE CONFUSED WITH R-domain (reductase to terminal aldehyde/alcohol)

    active = models.BooleanField(default=True)
    
    def operation(self, chain):

        if self.active == True:
            # make sure "zoline"-thioester moiety is present
            assert len(chain.GetSubstructMatches(chem.MolFromSmarts('C1=NC(C*1)C(=O)S'), useChirality=True)) == 1
            
            # checks if moiety to reduce is thiazoline - if so, reduces to thiazolidine
            if len(chain.GetSubstructMatches(chem.MolFromSmiles('C1=NC(CS1)C(=O)S'), useChirality=True)) == 1:
                rxn = AllChem.ReactionFromSmarts(('[C,c:11]C1=[N:6][CH1:7]([C:5]S1)[C:8](=[O:9])[S:10]>>'
                                                  '[C,c:11]C1[N:6][CH0:7]([C:5]S1)[C:8](=[O:9])[S:10]'))

            # checks if moiety to reduce is oxazoline - if so, oxidizes to oxazolidine
            elif len(chain.GetSubstructMatches(chem.MolFromSmiles('C1=NC(CO1)C(=O)S'), useChirality=True)) == 1:
                rxn = AllChem.ReactionFromSmarts(('[C,c:11]C1=[N:6][CH1:7]([C:5]O1)[C:8](=[O:9])[S:10]>>'
                                                  '[C,c:11]C1[N:6][CH0:7]([C:5]O1)[C:8](=[O:9])[S:10]'))
            else:
                raise Exception("This is a 'zoline' moiety currently unsupported. ")
            
            prod = rxn.RunReactants((chain,))[0][0]
            chem.SanitizeMol(prod)
            return prod
        
        else:
            return chain

    def __str__(self):
        return activityString(self)

    def __repr__(self):
        return ("Red")

class E(Domain):
    # Epimerization domain: Epimerizes L-amino acids to D-amino acids
    
    active = models.BooleanField(default=True)
    
    def operation(self, chain):
        # Does not work on thiazoline/oxazol type cyclic amino acids -- don't know if we'll see those cases
        
        # ensures if moiety to epimerize is a non-cyclized L-amino acid - if so, epimerizes to D-amino acid
        # Gly would throw error, smallest amino acid recognized is L-Ala
        if self.active == True:
            rxn = AllChem.ReactionFromSmarts(('[C:5][C@H:7]([N:6])[C:8](=[O:9])[S:10]>>'
                                              '[C:5][C@@H:7]([N:6])[C:8](=[O:9])[S:10]'))
            assert len(chain.GetSubstructMatches(chem.MolFromSmiles('C[C@H](N)C(=O)[S]'),
                   useChirality=True)) == 1, chem.MolToSmiles(chain)
            prod = rxn.RunReactants((chain,))[0][0]
            chem.SanitizeMol(prod)
            return prod
        else:
            return chain
    
    def __str__(self):
        return activityString(self)

    def __repr__(self):
        return ("E")

class nMT(Domain):
    # N-methylation domain: methylates amine
    
    active = models.BooleanField(default=True)
    
    def operation(self, chain):

        if self.active == True:
            rxn = AllChem.ReactionFromSmarts(('[N:6][C:7][C:8](=[O:9])[S:10]>>'
                                              '[N:6](C)[C:7][C:8](=[O:9])[S:10]'))
            
            # make sure there is only one nitrogen reaction site
            assert len(chain.GetSubstructMatches(chem.MolFromSmiles('NCC(=O)S'),
                       useChirality=True)) == 1, chem.MolToSmiles(chain)
            prod = rxn.RunReactants((chain,))[0][0]
            chem.SanitizeMol(prod)
            return prod
        else:
            return chain
    
    def __str__(self):
        return activityString(self)

    def __repr__(self):
        return ("nMT")

class F(Domain):
    # Formylation domain: formylates amine
    
    active = models.BooleanField(default=True)
    
    def operation(self, chain):

        if self.active == True:
            rxn = AllChem.ReactionFromSmarts(('[N:6][C:7][C:8](=[O:9])[S:10]>>'
                                              '[N:6](C(=O))[C:7][C:8](=[O:9])[S:10]'))
            
            # make sure there is only one nitrogen reaction site
            assert len(chain.GetSubstructMatches(chem.MolFromSmiles('NCC(=O)S'),
                       useChirality=True)) == 1, chem.MolToSmiles(chain)
            prod = rxn.RunReactants((chain,))[0][0]
            chem.SanitizeMol(prod)
            return prod
        else:
            return chain
    
    def __str__(self):
        return activityString(self)

    def __repr__(self):
        return ("F")

class AOX(Domain):
    # A domain interrupted by monooxygenase domain: alternative chain release forming amide (myxothiazol, melithiazol)
    # actual mechanism: adds glycine, hydroxylates alpha-carbon, then tautomerizes
    # TE releases subsequent glyoxylate from terminal PCP
    # NOT TO BE CONFUSED WITH P450-series MONOOXYGENASES (recruited by X domain)
    
    active = models.BooleanField(default=True)
    
    def operation(self, chain):

        if self.active == True:
            # forms amide from thioester (ignores actual mechanism)
            rxn = AllChem.ReactionFromSmarts(('[C:7][C:8](=[O:9])[S:10]>>'
                                              '[C:7][C:8](=[O:9])N.[S:10]'))
            
            # make sure there is only one nitrogen reaction site
            assert len(chain.GetSubstructMatches(chem.MolFromSmiles('CC(=O)S'),
                       useChirality=True)) == 1, chem.MolToSmiles(chain)
            prod = rxn.RunReactants((chain,))[0][0]
            chem.SanitizeMol(prod)
            return prod
        else:
            return chain
    
    def __str__(self):
        return activityString(self)

    def __repr__(self):
        return ("AOX")
    
class R(Domain):
    # Reductase domain: alternative chain release forming alcohol or aldehyde
    # Can act on NRP or PKS chains (e.g. coelimycin, BGC0000038)
    
    active = models.BooleanField(default=True)
    
    TYPE_CHOICES = (
        ('alcohol','alcohol'),
        ('aldehyde','aldehyde'),
    )
    type = models.CharField(
        max_length=8,
        choices=TYPE_CHOICES,
        default='alcohol',
        blank=False,
    )
    
    def operation(self, chain):

        if self.active == True:
            # Transformation determined by type
            if self.type == 'alcohol':
                # forms alcohol from thioester
                rxn = AllChem.ReactionFromSmarts(('[C:7][C:8](=[O:9])[S:10]>>'
                                                  '[C:7][C:8][O:9].[S:10]'))
                print("alcohol")
            elif self.type == 'aldehyde':
                # forms aldehyde from thioester
                rxn = AllChem.ReactionFromSmarts(('[C:7][C:8](=[O:9])[S:10]>>'
                                                  '[C:7][C:8](=[O:9]).[S:10]'))
                print("aldehyde")
            
            # this does not allow chemistry to work so cannot exit. default type set to alcohol
            # undefined type forces you to go to corrections file and define it manually
            #else:
            #    raise Exception("Undefined R domain type: go to the corrections file and manually define it as COH (alcohol) or CHO (aldehyde). ")
            
            # make sure there is only one thioester reaction site
            assert len(chain.GetSubstructMatches(chem.MolFromSmiles('CC(=O)S'),
                       useChirality=True)) == 1, chem.MolToSmiles(chain)
            prod = rxn.RunReactants((chain,))[0][0]
            chem.SanitizeMol(prod)
            return prod
        else:
            return chain
    
    def __str__(self):
        return "type %s, %s" % (self.type, activityString(self))

    def __repr__(self):
        return ("R")

class X(Domain):
    # P450 recruiter with ungeneralizable catalytic activity
    # activity depends on recruited P450
    
    active = models.BooleanField(default=True)
    
    def operation(self, chain):
        return chain
    
    def __str__(self):
        return activityString(self)

    def __repr__(self):
        return ("X")

class PCP(Domain):
    # Peptidyl carrier protein: links to intermediates

    def __str__(self):
        return "pcp domain"

    def __repr__(self):
        return("PCP")


class C(Domain):
    # Condensation domain: catalyzes "condensation" reaction under the A-domain

    # for differentiating between different types of C domains recognized by antismash
    TYPE_CHOICES = (
        ('Unknown', 'Unknown'),
        ('Starter', 'Starter'),
        ('LCL', 'LCL'),
        ('DCL', 'DCL'),
    )
    type = models.CharField(
        max_length=8,
        choices=TYPE_CHOICES,
        default=None,
        blank=False,
    )

    def __str__(self):
        return "type %s" % (self.type)

    def __repr__(self):
        return("C")