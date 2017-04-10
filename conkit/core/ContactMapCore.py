"""
Storage space for a contact map
"""

from __future__ import division

__author__ = "Felix Simkovic"
__credits__ = "Jens Thomas"
__date__ = "03 Aug 2016"
__version__ = 0.1

from conkit.core.EntityCore import Entity
from conkit.core.SequenceCore import Sequence

import collections
import numpy
import warnings

try:
    import sklearn.neighbors
    SKLEARN = True
except ImportError:
    SKLEARN = False


class _BandwidthEstimators(object):
    """A collection of bandwidth estimators for Kernel Density Estimation"""
    @staticmethod
    def amise(p, niterations=25, eps=1e-3):

        def curvature(p, x, w):
            z = (x - p) / w
            y = (1 * (z ** 2 - 1.0) * numpy.exp(-0.5 * z * z) / (w * numpy.sqrt(2. * numpy.pi)) / w ** 2).sum()
            return y / p.shape[0]

        def extended_range(mn, mx, bw, ext=3):
            return mn - ext * bw, mx + ext * bw

        def optimal_bandwidth_equation(p, default_bw):
            alpha = 1. / (2. * numpy.sqrt(numpy.pi))
            sigma = 1.0
            n = p.shape[0]
            q = stiffness_integral(p, default_bw)
            return default_bw - ((n * q * sigma ** 4) / alpha) ** (-1.0 / (p.shape[1] + 4))

        def stiffness_integral(p, default_bw, eps=1e-4):
            mn, mx = extended_range(p.min(), p.max(), default_bw, ext=3)
            n = 1
            dx = (mx - mn) / n
            yy = 0.5 * dx * (curvature(p, mn, default_bw) ** 2 +
                             curvature(p, mx, default_bw) ** 2)
            # The trapezoidal rule guarantees a relative error of better than eps
            # for some number of steps less than maxn.
            maxn = (mx - mn) / numpy.sqrt(eps)
            # Cap the total computation spent
            maxn = 2048 if maxn > 2048 else maxn
            n = 2
            while n <= maxn:
                dx /= 2.
                y = 0
                for i in numpy.arange(1, n, 2):
                    y += curvature(p, mn + i * dx, default_bw) ** 2
                yy = 0.5 * yy + y * dx
                if n > 8 and abs(y * dx - 0.5 * yy) < eps * yy:
                    break
                n *= 2
            return yy

        x0 = _BandwidthEstimators.bowman(p)
        y0 = optimal_bandwidth_equation(p, x0)

        x = 0.8 * x0
        y = optimal_bandwidth_equation(p, x)

        for _ in numpy.arange(niterations):
            x -= y * (x0 - x) / (y0 - y)
            y = optimal_bandwidth_equation(p, x)
            if abs(y) < (eps * y0):
                break
        return x

    @staticmethod
    def bowman(p):
        sigma = numpy.sqrt((p ** 2).sum() / p.shape[0] - (p.sum() / p.shape[0]) ** 2)
        return sigma * ((((p.shape[1] + 2) * p.shape[0]) / 4.) ** (-1. / (p.shape[1] + 4)))

    @staticmethod
    def scott(p):
        sigma = numpy.minimum(
            numpy.std(p, axis=0, ddof=1),
            (numpy.percentile(p, 75) - numpy.percentile(p, 25)) / 1.349
        ).astype(numpy.float64)
        return 1.059 * sigma * p.shape[0] ** (-1. / (p.shape[1] + 4))

    @staticmethod
    def silverman(p):
        sigma = numpy.minimum(
            numpy.std(p, axis=0, ddof=1),
            (numpy.percentile(p, 75) - numpy.percentile(p, 25)) / 1.349
        ).astype(numpy.float64)
        return 0.9 * sigma * (p.shape[0] * (p.shape[1] + 2) / 4.) ** (-1. / (p.shape[1] + 4))


class _Residue(object):
    """A basic class representing a residue"""
    __slots__ = ('res_seq', 'res_altseq', 'res_name', 'res_chain')

    def __init__(self, res_seq, res_altseq, res_name, res_chain):
        self.res_seq = res_seq
        self.res_altseq = res_altseq
        self.res_name = res_name
        self.res_chain = res_chain

    def __repr__(self):
        string = "{0}(res_seq='{1}' res_altseq='{2}' res_name='{3}' res_chain='{4}')"
        return string.format(
                self.__class__.__name__, self.res_seq, 
                self.res_altseq, self.res_name, self.res_chain
        )


class _Gap(object):
    """A basic class representing a gap residue"""
    __slots__ = ('res_seq', 'res_altseq', 'res_name', 'res_chain')

    _IDENTIFIER = -999999

    def __init__(self):
        self.res_seq = _Gap._IDENTIFIER
        self.res_altseq = _Gap._IDENTIFIER
        self.res_name = 'X'
        self.res_chain = ''

    def __repr__(self):
        string = "{0}(res_seq='{1}' res_altseq='{2}' res_name='{3}' res_chain='{4}')"
        return string.format(
                self.__class__.__name__, self.res_seq, 
                self.res_altseq, self.res_name, self.res_chain
        )


class ContactMap(Entity):
    """A contact map object representing a single prediction

    The :obj:`ContactMap <conkit.core.ContactMap>` class represents a data structure to hold a single
    contact map prediction in one place. It contains functions to store,
    manipulate and organise :obj:`Contact <conkit.core.Contact>` instances.

    Attributes
    ----------
    coverage : float
       The sequence coverage score
    id : str
       A unique identifier
    ncontacts : int
       The number of :obj:`Contact <conkit.core.Contact>` instances in the :obj:`ContactMap <conkit.core.ContactMap>`
    precision : float
       The precision (Positive Predictive Value) score
    repr_sequence : :obj:`Sequence <conkit.core.Sequence>`
       The representative :obj:`Sequence <conkit.core.Sequence>` associated with the :obj:`ContactMap <conkit.core.ContactMap>`
    repr_sequence_altloc : :obj:`Sequence <conkit.core.Sequence>`
       The representative altloc :obj:`Sequence <conkit.core.Sequence>` associated with the :obj:`ContactMap <conkit.core.ContactMap>`
    sequence : :obj:`Sequence <conkit.core.Sequence>`
       The :obj:`Sequence <conkit.core.Sequence>` associated with the :obj:`ContactMap <conkit.core.ContactMap>`
    top_contact : :obj:`Contact <conkit.core.Contact>`
       The first :obj:`Contact <conkit.core.Contact>` entry in :obj:`ContactMap <conkit.core.ContactMap>`

    Examples
    --------
    >>> from conkit.core import Contact, ContactMap
    >>> contact_map = ContactMap("example")
    >>> contact_map.add(Contact(1, 10, 0.333))
    >>> contact_map.add(Contact(5, 30, 0.667))
    >>> print(contact_map)
    ContactMap(id="example" ncontacts=2)

    """
    __slots__ = ['_sequence']

    def __init__(self, id):
        """Initialise a new contact map"""
        self._sequence = None
        super(ContactMap, self).__init__(id)

    def __repr__(self):
        return "{0}(id=\"{1}\", ncontacts={2})".format(
                self.__class__.__name__, self.id, self.ncontacts
        )

    @property
    def coverage(self):
        """The sequence coverage score

        The coverage score is calculated by analysing the number of residues
        covered by the predicted contact pairs.

        .. math::

           Coverage=\\frac{x_{cov}}{L}

        The coverage score is calculated by dividing the number of contacts
        :math:`x_{cov}` by the number of residues in the sequence :math:`L`.

        Returns
        -------
        cov : float
           The calculated coverage score

        See Also
        --------
        precision

        """
        seq_array = numpy.fromstring(self.repr_sequence.seq, dtype='uint8')
        gaps = numpy.where(seq_array == ord('-'), 1, 0)
        cov = (seq_array.size - numpy.sum(gaps, axis=0)) / seq_array.size
        return cov

    @property
    def ncontacts(self):
        """The number of :obj:`Contact <conkit.core.Contact>` instances in the :obj:`ContactMap <conkit.core.ContactMap>`

        Returns
        -------
        ncontacts : int
           The number of sequences in the :obj:`ContactMap <conkit.core.ContactMap>`

        """
        return len(self)

    @property
    def precision(self):
        """The precision (Positive Predictive Value) score

        The precision value is calculated by analysing the true and false
        postive contacts.

        .. math::

           Precision=\\frac{TruePositives}{TruePositives - FalsePositives}

        The status of each contact, i.e true or false positive status, can be
        determined by running the :func:`match` function providing a reference
        structure.

        Returns
        -------
        ppv : float
           The calculated precision score

        See Also
        --------
        coverage

        """
        status_array = numpy.asarray([c.status for c in self])

        fp_count = numpy.sum(numpy.where(status_array == -1, 1, 0))
        uk_count = numpy.sum(numpy.where(status_array == 0, 1, 0))
        tp_count = numpy.sum(numpy.where(status_array == 1, 1, 0))

        # ContactMap is empty
        if len(self) == 0:
            return 0.0
        elif fp_count == 0.0 and tp_count == 0.0:
            warnings.warn("No matches or mismatches found in your contact map. Match two ContactMaps first.")
            return 0.0
        elif uk_count > 0:
            warnings.warn("Some contacts between the ContactMaps are unmatched due to non-identical "
                          "sequences. The precision value might be inaccurate.")

        return tp_count / (tp_count + fp_count)

    @property
    def repr_sequence(self):
        """The representative :obj:`Sequence <conkit.core.Sequence>` associated with the :obj:`ContactMap <conkit.core.ContactMap>`

        The peptide sequence constructed from the available
        contacts using the normal res_seq positions

        Returns
        -------
        sequence : :obj:`conkit.coreSequence`

        Raises
        ------
        TypeError
           Sequence undefined

        See Also
        --------
        repr_sequence_altloc, sequence

        """
        if not isinstance(self.sequence, Sequence):
            raise TypeError('Define the sequence as Sequence() instance')
        # Get all resseqs that are the contact map
        res1_seqs, res2_seqs = list(zip(*[contact.id for contact in self]))
        res_seqs = set(
            sorted(res1_seqs + res2_seqs)
        )
        return self._construct_repr_sequence(list(res_seqs))

    @property
    def repr_sequence_altloc(self):
        """The representative altloc :obj:`Sequence <conkit.core.Sequence>` associated with the :obj:`ContactMap <conkit.core.ContactMap>`

        The peptide sequence constructed from the available
        contacts using the altloc res_seq positions

        Returns
        -------
        sequence : :obj:`Sequence <conkit.core.Sequence>`

        Raises
        ------
        ValueError
           Sequence undefined

        See Also
        --------
        repr_sequence, sequence

        """
        if not isinstance(self.sequence, Sequence):
            raise TypeError('Define the sequence as Sequence() instance')
        # Get all resseqs that are the contact map
        res1_seqs, res2_seqs = list(zip(*[(contact.res1_altseq, contact.res2_altseq) for contact in self]))
        res_seqs = set(
            sorted(res1_seqs + res2_seqs)
        )
        return self._construct_repr_sequence(list(res_seqs))

    @property
    def sequence(self):
        """The :obj:`Sequence <conkit.core.Sequence>` associated with the :obj:`ContactMap <conkit.core.ContactMap>`

        Returns
        -------
        :obj:`Sequence <conkit.core.Sequence>`

        See Also
        --------
        repr_sequence, repr_sequence_altloc

        """
        return self._sequence

    @sequence.setter
    def sequence(self, sequence):
        """Associate a :obj:`Sequence <conkit.core.Sequence>` instance with the :obj:`ContactMap <conkit.core.ContactMap>`

        Parameters
        ----------
        sequence : :obj:`Sequence <conkit.core.Sequence>`

        Raises
        ------
        ValueError
           Incorrect hierarchy instance provided

        """
        if not isinstance(sequence, Sequence):
            raise TypeError('Instance of Sequence() required: {0}'.format(sequence))
        self._sequence = sequence

    @property
    def top_contact(self):
        """The first :obj:`Contact <conkit.core.Contact>` entry in :obj:`ContactMap <conkit.core.ContactMap>`

        Returns
        -------
        top_contact : :obj:`Contact <conkit.core.Contact>`, None
           The first :obj:`Contact <conkit.core.Contact>` entry in :obj:`ContactFile <conkit.core.ContactFile>`

        """
        if len(self) > 0:
            return self[0]
        else:
            return None

    def _construct_repr_sequence(self, res_seqs):
        """Construct the representative sequence"""
        # Determine which are present and which are not
        representative_sequence = ''
        for i in range(1, self.sequence.seq_len + 1):
            if i in res_seqs:
                representative_sequence += self.sequence.seq[i - 1]
            else:
                representative_sequence += '-'
        return Sequence(self.sequence.id + '_repr', representative_sequence)

    def assign_sequence_register(self, altloc=False):
        """Assign the amino acids from :obj:`Sequence <conkit.core.Sequence>` to all :obj:`Contact <conkit.core.Contact>` instances

        Parameters
        ----------
        altloc : bool
           Use the res_altloc positions [default: False]

        """
        for c in self:
            if altloc:
                res1_index, res2_index = c.res1_altseq, c.res2_altseq
            else:
                res1_index, res2_index = c.res1_seq, c.res2_seq
            c.res1 = self.sequence.seq[res1_index - 1]
            c.res2 = self.sequence.seq[res2_index - 1]

    def calculate_jaccard_index(self, other):
        """Calculate the Jaccard index between two :obj:`ContactMap <conkit.core.ContactMap>` instances

        This score analyzes the difference of the predicted contacts from two maps,

        .. math::

           J_{x,y}=\\frac{\\left|x \\cap y\\right|}{\\left|x \\cup y\\right|}
    
        where :math:`x` and :math:`y` are the sets of predicted contacts from two 
        different predictors, :math:`\\left|x \\cap y\\right|` is the number of 
        elements in the intersection of :math:`x` and :math:`y`, and the 
        :math:`\\left|x \\cup y\\right|` represents the number of elements in the 
        union of :math:`x` and :math:`y`.

        The J-score has values in the range of :math:`[0, 1]`, with a value of :math:`1` 
        corresponding to identical contact maps and :math:`0` to dissimilar ones.

        Parameters
        ----------
        other : :obj:`ContactMap <conkit.core.ContactMap>`
           A ConKit :obj:`ContactMap <conkit.core.ContactMap>`
        
        Returns
        -------
        float
           The Jaccard distance

        See Also
        --------
        match, precision
        
        Warnings
        --------
        The Jaccard distance ranges from :math:`[0, 1]`, where :math:`1` means 
        the maps contain identical contacts pairs.

        Notes
        -----
        The Jaccard index is different from the Jaccard distance mentioned in [#]_. The
        Jaccard distance corresponds to :math:`1-Jaccard_{index}`.

        .. [#] Q. Wuyun, W. Zheng, Z. Peng, J. Yang (2016). A large-scale comparative assessment
           of methods for residue-residue contact prediction. *Briefings in Bioinformatics*,
           [doi: 10.1093/bib/bbw106].

        """
        intersection = numpy.sum([1 for contact in self if contact.id in other])
        union = len(self) + numpy.sum([1 for contact in other if contact.id not in self])
        # If self and other are both empty, we define J(x,y) = 1
        if union == 0:
            return 1.0
        return float(intersection) / union

    def calculate_kernel_density(self, bw_method="amise"):
        """Calculate the contact density in the contact map using Gaussian kernels

        Various algorithms can be used to estimate the bandwidth. To calculate the
        bandwidth for an 1D data array ``X`` with ``n`` data points and ``d`` dimensions,
        the listed algorithms have been implemented. Please note, in rules 2 and 3, the
        value of :math:`\\sigma` is the smaller of the standard deviation of ``X`` or
        the normalized interquartile range.

        1. Asymptotic Mean Integrated Squared Error (AMISE)

           This particular choice of bandwidth recovers all the important features whilst maintaining smoothness. 
           It is a direct implementation of the method used by [#]_.


        2. Bowman & Azzalini [#]_ implementation

        .. math::

           \\sqrt{\\frac{\\sum{X}^2}{n}-(\\frac{\\sum{X}}{n})^2}*(\\frac{(d+2)*n}{4})^\\frac{-1}{d+4}

        3. Scott's [#]_ implementation

        .. math::

           1.059*\\sigma*n^\\frac{-1}{d+4}
        4. Silverman's [#]_ implementation

        .. math::

           0.9*\\sigma*(n*\\frac{d+2}{4})^\\frac{-1}{d+4}

        .. [#] Sadowski, M.I. (2013). Prediction of protein domain boundaries from inverse covariances.
        .. [#] Bowman, A.W. & Azzalini, A. (1997). Applied Smoothing Techniques for Data Analysis.
        .. [#] Scott, D.W. (1992). Multivariate Density Estimation: Theory, Practice, and Visualization.
        .. [#] Silverman, B.W. (1986). Density Estimation for Statistics and Data Analysis.

        Parameters
        ----------
        bw_method : str, optional
           The bandwidth estimator to use [default: amise_sekant]

        Returns
        -------
        list
           The list of per-residue density estimates

        Raises
        ------
        RuntimeError
           Cannot find SciKit package
        ValueError
           Undefined bandwidth method

        """
        if not SKLEARN:
            raise RuntimeError('Cannot find SciKit package')

        # Compute the relevant data we need
        x = numpy.asarray([i for c in self for i in numpy.arange(c.res1_seq, c.res2_seq)])[:, numpy.newaxis]
        x_fit = numpy.linspace(x.min(), x.max() + 1, x.max() - x.min() + 1)[:, numpy.newaxis]

        # Obtain the bandwidth as defined by user method
        if bw_method == "amise":
            bandwidth = _BandwidthEstimators.amise(x)
        elif bw_method == "bowman":
            bandwidth = _BandwidthEstimators.bowman(x)
        elif bw_method == "scott":
            bandwidth = _BandwidthEstimators.scott(x)
        elif bw_method == "silverman":
            bandwidth = _BandwidthEstimators.silverman(x)
        else:
            msg = "Undefined bandwidth method: {0}".format(bw_method)
            raise ValueError(msg)

        # Estimate the Kernel Density using original data and fit random sample
        kde = sklearn.neighbors.KernelDensity(bandwidth=bandwidth).fit(x)
        return numpy.exp(kde.score_samples(x_fit)).tolist()

    def calculate_scalar_score(self):
        """Calculate a scaled score for the :obj:`ContactMap <conkit.core.ContactMap>`

        This score is a scaled score for all raw scores in a contact
        map. It is defined by the formula

        .. math::

           {x}'=\\frac{x}{\\overline{d}}

        where :math:`x` corresponds to the raw score of each predicted
        contact and :math:`\overline{d}` to the mean of all raw scores.

        The score is saved in a separate :obj:`Contact <conkit.core.Contact>` attribute called
        ``scalar_score``

        This score is described in more detail in [#]_.

        .. [#] S. Ovchinnikov, L. Kinch, H. Park, Y. Liao, J. Pei, D.E. Kim,
           H. Kamisetty, N.V. Grishin, D. Baker (2015). Large-scale determination
           of previously unsolved protein structures using evolutionary information.
           *Elife* **4**, e09248.

        """
        raw_scores = numpy.asarray([c.raw_score for c in self])
        sca_scores = raw_scores / numpy.mean(raw_scores)
        for contact, sca_score in zip(self, sca_scores):
            contact.scalar_score = sca_score
        return

    def find(self, indexes, altloc=False):
        """Find all contacts associated with ``index``

        Parameters
        ----------
        index : list, tuple
           A list of residue indexes to find
        altloc : bool
           Use the res_altloc positions [default: False]

        Returns
        -------
        :obj:`ContactMap <conkit.core.ContactMap>`
           A modified version of the contact map containing
           the found contacts

        """
        contact_map = self.copy()
        for contact in self:
            if altloc and (contact.res1_altseq in indexes or contact.res2_altseq in indexes):
                continue
            elif contact.res1_seq in indexes or contact.res2_seq in indexes:
                continue
            else:
                contact_map.remove(contact.id)
        return contact_map

    def match(self, other, remove_unmatched=False, renumber=False, inplace=False):
        """Modify both hierarchies so residue numbers match one another.

        This function is key when plotting contact maps or visualising
        contact maps in 3-dimensional space. In particular, when residue
        numbers in the structure do not start at count 0 or when peptide
        chain breaks are present.

        Parameters
        ----------
        other : :obj:`ContactMap <conkit.core.ContactMap>`
           A ConKit :obj:`ContactMap <conkit.core.ContactMap>`
        remove_unmatched : bool, optional
           Remove all unmatched contacts [default: False]
        renumber : bool, optional
           Renumber the res_seq entries [default: False]

           If ``True``, ``res1_seq`` and ``res2_seq`` changes
           but ``id`` remains the same
        inplace : bool, optional
           Replace the saved order of contacts [default: False]

        Returns
        -------
        hierarchy_mod
            :obj:`ContactMap <conkit.core.ContactMap>` instance, regardless of inplace

        Raises
        ------
        ValueError
           Error creating reliable keymap matching the sequence in :obj:`ContactMap <conkit.core.ContactMap>`

        """
        contact_map1 = self._inplace(inplace)
        contact_map2 = other._inplace(inplace)

        # ================================================================
        # 1. Align all sequences
        # ================================================================

        # Align both full sequences against each other
        aligned_sequences_full = contact_map1.sequence.align_local(contact_map2.sequence, id_chars=2,
                                                                   nonid_chars=1, gap_open_pen=-0.5,
                                                                   gap_ext_pen=-0.1)
        contact_map1_full_sequence, contact_map2_full_sequence = aligned_sequences_full

        # Align contact map 1 full sequences with representative sequence
        aligned_sequences_map1 = contact_map1_full_sequence.align_local(contact_map1.repr_sequence,
                                                                        id_chars=2, nonid_chars=1, gap_open_pen=-0.5,
                                                                        gap_ext_pen=-0.2, inplace=True)
        contact_map1_repr_sequence = aligned_sequences_map1[-1]

        # Align contact map 2 full sequences with __ALTLOC__ representative sequence
        aligned_sequences_map2 = contact_map2_full_sequence.align_local(contact_map2.repr_sequence_altloc,
                                                                        id_chars=2, nonid_chars=1, gap_open_pen=-0.5,
                                                                        gap_ext_pen=-0.2, inplace=True)
        contact_map2_repr_sequence = aligned_sequences_map2[-1]

        # Align both aligned representative sequences
        aligned_sequences_repr = contact_map1_repr_sequence.align_local(contact_map2_repr_sequence,
                                                                        id_chars=2, nonid_chars=1, gap_open_pen=-1.0,
                                                                        gap_ext_pen=-0.5, inplace=True)
        contact_map1_repr_sequence, contact_map2_repr_sequence = aligned_sequences_repr

        # ================================================================
        # 2. Identify TPs in other, map them, and match them to self
        # ================================================================

        # Encode the sequences to uint8 character arrays for easier and faster handling
        encoded_repr = numpy.asarray([
            numpy.fromstring(contact_map1_repr_sequence.seq, dtype='uint8'),
            numpy.fromstring(contact_map2_repr_sequence.seq, dtype='uint8')
        ])

        # Create mappings for both contact maps
        contact_map1_keymap = ContactMap._create_keymap(contact_map1)
        contact_map2_keymap = ContactMap._create_keymap(contact_map2, altloc=True)

        # Some checks
        msg = "Error creating reliable keymap matching the sequence in ContactMap: "
        if len(contact_map1_keymap) != numpy.where(encoded_repr[0] != ord('-'))[0].shape[0]:
            msg += contact_map1.id
            raise ValueError(msg)
        elif len(contact_map2_keymap) != numpy.where(encoded_repr[1] != ord('-'))[0].shape[0]:
            msg += contact_map2.id
            raise ValueError(msg)

        # Create a sequence matching keymap including deletions and insertions
        contact_map1_keymap = ContactMap._insert_states(encoded_repr[0], contact_map1_keymap)
        contact_map2_keymap = ContactMap._insert_states(encoded_repr[1], contact_map2_keymap)

        # Reindex the altseq positions to account for insertions/deletions
        contact_map1_keymap = ContactMap._reindex(contact_map1_keymap)
        contact_map2_keymap = ContactMap._reindex(contact_map2_keymap)

        # Adjust the res_altseq based on the insertions and deletions
        contact_map2 = ContactMap._adjust(contact_map2, contact_map2_keymap)

        # Get the residue list for matching UNKNOWNs
        residues_map2 = tuple(i+1 for i, a in enumerate(aligned_sequences_full[1].seq) if a != '-')

        # Adjust true and false positive statuses
        for contact in contact_map1:
            id = (contact.res1_seq, contact.res2_seq)
            id_alt = tuple(r.res_seq for r in contact_map2_keymap for i in id if i == r.res_altseq)

            if any(i == _Gap._IDENTIFIER for i in id_alt) and any(j not in residues_map2 for j in id):
                contact_map1[id].define_unknown()
            elif all(i in residues_map2 for i in id):
                if id_alt in contact_map2:
                    contact_map1[id].define_match()
                else:
                    contact_map1[id].define_mismatch()
            else:
                msg = "Error matching two contact maps - this should never happen"
                raise RuntimeError(msg)

        # ================================================================
        # 3. Remove unmatched contacts
        # ================================================================
        if remove_unmatched:
            for contact in contact_map1.copy():
                if contact.is_unknown:
                    contact_map1.remove(contact.id)

        # ================================================================
        # 4. Renumber the contact map 1 based on contact map 2
        # ================================================================
        if renumber:
            contact_map1 = ContactMap._renumber(contact_map1, contact_map1_keymap, contact_map2_keymap)

        return contact_map1

    def remove_neighbors(self, min_distance=5, inplace=False):
        """Remove contacts between neighboring residues

        Parameters
        ----------
        min_distance : int, optional
           The minimum number of residues between contacts  [default: 5]
        inplace : bool, optional
           Replace the saved order of contacts [default: False]

        Returns
        -------
        contact_map : :obj:`ContactMap <conkit.core.ContactMap>`
           The reference to the :obj:`ContactMap <conkit.core.ContactMap>`, regardless of inplace

        """
        contact_map = self._inplace(inplace)
        for contact in contact_map.copy():
            if abs(contact.res1_seq - contact.res2_seq) < min_distance:
                contact_map.remove(contact.id)
        return contact_map

    def rescale(self, inplace=False):
        """Rescale the raw scores in :obj:`ContactMap <conkit.core.ContactMap>`

        Rescaling of the data is done to normalize the raw scores
        to be in the range [0, 1]. The formula to rescale the data is:

        .. math::

           {x}'=\\frac{x-min(d)}{max(d)-min(d)}

        :math:`x` is the original value and :math:`d` are all values to be
        rescaled.

        Parameters
        ----------
        inplace : bool, optional
           Replace the saved order of contacts [default: False]

        Returns
        -------
        contact_map : :obj:`ContactMap <conkit.core.ContactMap>`
           The reference to the :obj:`ContactMap <conkit.core.ContactMap>`, regardless of inplace

        """
        contact_map = self._inplace(inplace)

        raw_scores = numpy.asarray([c.raw_score for c in contact_map])
        norm_raw_scores = (raw_scores - raw_scores.min()) / (raw_scores.max() - raw_scores.min())

        # Important to not end up with raw scores == numpy.nan
        if numpy.isnan(norm_raw_scores).all():
            norm_raw_scores = numpy.where(norm_raw_scores == numpy.isnan, 0, 1)

        for contact, norm_raw_score in zip(contact_map, norm_raw_scores):
            contact.raw_score = norm_raw_score

        return contact_map

    def sort(self, kword, reverse=False, inplace=False):
        """Sort the :obj:`ContactMap <conkit.core.ContactMap>`

        Parameters
        ----------
        kword : str
           The dictionary key to sort contacts by
        reverse : bool, optional
           Sort the contact pairs in descending order [default: False]
        inplace : bool, optional
           Replace the saved order of contacts [default: False]

        Returns
        -------
        contact_map : :obj:`ContactMap <conkit.core.ContactMap>`
           The reference to the :obj:`ContactMap <conkit.core.ContactMap>`, regardless of inplace

        Raises
        ------
        ValueError
           ``kword`` not in :obj:`ContactMap <conkit.core.ContactMap>`

        """
        contact_map = self._inplace(inplace)
        contact_map._sort(kword, reverse)
        return contact_map

    @staticmethod
    def _adjust(contact_map, keymap):
        """Adjust res_altseq entries to insertions and deletions"""
        encoder = dict((x.res_seq, x.res_altseq) for x in keymap if isinstance(x, _Residue))
        for contact in contact_map:
            if contact.res1_seq in list(encoder.keys()):
                contact.res1_altseq = encoder[contact.res1_seq]
            if contact.res2_seq in list(encoder.keys()):
                contact.res2_altseq = encoder[contact.res2_seq]
        return contact_map

    @staticmethod
    def _create_keymap(contact_map, altloc=False):
        """Create a simple keymap

        Parameters
        ----------
        altloc : bool
           Use the res_altloc positions [default: False]

        Returns
        -------
        list
           A list of residue mappings

        """
        contact_map_keymap = collections.OrderedDict()
        for contact in contact_map:
            pos1 = _Residue(contact.res1_seq, contact.res1_altseq, contact.res1, contact.res1_chain)
            pos2 = _Residue(contact.res2_seq, contact.res2_altseq, contact.res2, contact.res2_chain)
            if altloc:
                res1_index, res2_index = contact.res1_altseq, contact.res2_altseq
            else:
                res1_index, res2_index = contact.res1_seq, contact.res2_seq
            contact_map_keymap[res1_index] = pos1
            contact_map_keymap[res2_index] = pos2
        contact_map_keymap_sorted = sorted(list(contact_map_keymap.items()), key=lambda x: int(x[0]))
        return list(zip(*contact_map_keymap_sorted))[1]

    @staticmethod
    def _find_single(contact_map, index):
        """Find all contacts associated with ``index`` based on id property"""
        for c in contact_map:
            if c.id[0] == index or c.id[1] == index:
                yield c

    @staticmethod
    def _insert_states(sequence, keymap):
        """Create a sequence matching keymap including deletions and insertions"""
        it = iter(keymap)
        keymap_ = []
        for amino_acid in sequence:
            if amino_acid == ord('-'):
                keymap_.append(_Gap())
            else:
                keymap_.append(next(it))
        return keymap_

    @staticmethod
    def _reindex(keymap):
        """Reindex a key map"""
        for i, residue in enumerate(keymap):
            residue.res_altseq = i + 1
        return keymap

    @staticmethod
    def _renumber(contact_map, self_keymap, other_keymap):
        """Renumber the contact map based on the mapping of self and other keymaps"""
        for self_residue, other_residue in zip(self_keymap, other_keymap):
            if isinstance(self_residue, _Gap):
                continue
            for contact in ContactMap._find_single(contact_map, self_residue.res_seq):
                # Make sure we check with the ID, which doesn't change
                if contact.id[0] == self_residue.res_altseq:
                    contact.res1_seq = other_residue.res_seq
                    contact.res1_chain = other_residue.res_chain
                elif contact.id[1] == self_residue.res_altseq:
                    contact.res2_seq = other_residue.res_seq
                    contact.res2_chain = other_residue.res_chain
                else:
                    raise ValueError('Should never get here')

        return contact_map