# Generated by Django 2.2.4 on 2022-09-14 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='a',
            name='substrate',
            field=models.CharField(choices=[('a3abut', 'a3abut'), ('mthz', 'mthz'), ('butmal', 'butmal'), ('leu', 'leu'), ('8C-AA', '8C-AA'), ('d-arg', 'd-arg'), ('benz', 'benz'), ('d-lys', 'd-lys'), ('be-14106-1', 'be-14106-1'), ('butylamine', 'butylamine'), ('cremimycin1', 'cremimycin1'), ('pro', 'pro'), ('PABA', 'PABA'), ('propylamine', 'propylamine'), ('d-glu-2', 'd-glu-2'), ('ml-449-1', 'ml-449-1'), ('asp', 'asp'), ('gly', 'gly'), ('cys', 'cys'), ('isobutmal', 'isobutmal'), ('AHBA', 'AHBA'), ('2-oxobutmal', '2-oxobutmal'), ('d-asp', 'd-asp'), ('mxmal_ACP', 'mxmal_ACP'), ('mpro', 'mpro'), ('ser', 'ser'), ('beta-OH-asn', 'beta-OH-asn'), ('hpg', 'hpg'), ('ethylguanidine', 'ethylguanidine'), ('d-trp', 'd-trp'), ('d-tyr', 'd-tyr'), ('cemal', 'cemal'), ('hpla', 'hpla'), ('3-me-hexmal', '3-me-hexmal'), ('o-hydroxybenz', 'o-hydroxybenz'), ('htyr', 'htyr'), ('methylbenz', 'methylbenz'), ('vinylcinnamoyl', 'vinylcinnamoyl'), ('2-etmalonamyl', '2-etmalonamyl'), ('asn', 'asn'), ('glu', 'glu'), ('NH2', 'NH2'), ('isobut', 'isobut'), ('2aminopent', '2aminopent'), ('3cl-tyr', '3cl-tyr'), ('heronamide-1', 'heronamide-1'), ('bmt', 'bmt'), ('dap', 'dap'), ('d-met', 'd-met'), ('alpha-OH-phe', 'alpha-OH-phe'), ('emal', 'emal'), ('AAnon', 'AAnon'), ('trans-1,2-CPDA', 'trans-1,2-CPDA'), ('ile', 'ile'), ('lipopep-8D1-1', 'lipopep-8D1-1'), ('dhb', 'dhb'), ('ema', 'ema'), ('butylguanidine', 'butylguanidine'), ('mmal', 'mmal'), ('d-ile', 'd-ile'), ('mal', 'mal'), ('guan', 'guan'), ('alpha-OH-htyr', 'alpha-OH-htyr'), ('me-tyr', 'me-tyr'), ('gln', 'gln'), ('isoval', 'isoval'), ('val', 'val'), ('DHCHene', 'DHCHene'), ('allylmal', 'allylmal'), ('methylbenz-val', 'methylbenz-val'), ('beta-amino-glu', 'beta-amino-glu'), ('cyclopentene', 'cyclopentene'), ('d-leu', 'd-leu'), ('pyr', 'pyr'), ('16C-FA', '16C-FA'), ('me-glu', 'me-glu'), ('prop', 'prop'), ('14C-FA', '14C-FA'), ('d-gln', 'd-gln'), ('Acetyl-CoA', 'Acetyl-CoA'), ('3measp', '3measp'), ('d-pro', 'd-pro'), ('end', 'end'), ('fatty_acid', 'fatty_acid'), ('ala', 'ala'), ('beta-amino-phe', 'beta-amino-phe'), ('2356-OH-me-benz', '2356-OH-me-benz'), ('d-ser', 'd-ser'), ('mxmal', 'mxmal'), ('hexmal', 'hexmal'), ('piperazic', 'piperazic'), ('d-cys', 'd-cys'), ('m-tyr', 'm-tyr'), ('d-phe', 'd-phe'), ('lys', 'lys'), ('d-val', 'd-val'), ('arg-AA', 'arg-AA'), ('dpg', 'dpg'), ('choi', 'choi'), ('PNBA', 'PNBA'), ('d-asn', 'd-asn'), ('beta-OH-tyr', 'beta-OH-tyr'), ('met', 'met'), ('arg', 'arg'), ('thr', 'thr'), ('d-ala', 'd-ala'), ('gamma-OH-lys', 'gamma-OH-lys'), ('me-PABA', 'me-PABA'), ('d-glu', 'd-glu'), ('DCP', 'DCP'), ('2metbut', '2metbut'), ('orn', 'orn'), ('his', 'his'), ('asp-2', 'asp-2'), ('kyn', 'kyn'), ('shikimic_acid', 'shikimic_acid'), ('3aminobut', '3aminobut'), ('trp', 'trp'), ('cin', 'cin'), ('me-pro', 'me-pro'), ('phe', 'phe'), ('N-OH-orn', 'N-OH-orn'), ('10C-FA', '10C-FA'), ('CHC-CoA', 'CHC-CoA'), ('pip', 'pip'), ('hse', 'hse'), ('beta-OH-asp', 'beta-OH-asp'), ('d-his', 'd-his'), ('D-isobutmal', 'D-isobutmal'), ('d-thr', 'd-thr'), ('me-asp', 'me-asp'), ('plac', 'plac'), ('DHCH', 'DHCH'), ('hmal', 'hmal'), ('N/A', 'N/A'), ('aba', 'aba'), ('tyr', 'tyr'), ('6-me-hexyl-thr', '6-me-hexyl-thr'), ('dab', 'dab')], default='gly', max_length=25),
        ),
        migrations.AlterField(
            model_name='acp',
            name='substrate',
            field=models.CharField(choices=[('a3abut', 'a3abut'), ('mthz', 'mthz'), ('butmal', 'butmal'), ('leu', 'leu'), ('8C-AA', '8C-AA'), ('d-arg', 'd-arg'), ('benz', 'benz'), ('d-lys', 'd-lys'), ('be-14106-1', 'be-14106-1'), ('butylamine', 'butylamine'), ('cremimycin1', 'cremimycin1'), ('pro', 'pro'), ('PABA', 'PABA'), ('propylamine', 'propylamine'), ('d-glu-2', 'd-glu-2'), ('ml-449-1', 'ml-449-1'), ('asp', 'asp'), ('gly', 'gly'), ('cys', 'cys'), ('AHBA', 'AHBA'), ('d-asp', 'd-asp'), ('mxmal_ACP', 'mxmal_ACP'), ('mpro', 'mpro'), ('ser', 'ser'), ('beta-OH-asn', 'beta-OH-asn'), ('hpg', 'hpg'), ('ethylguanidine', 'ethylguanidine'), ('d-trp', 'd-trp'), ('d-tyr', 'd-tyr'), ('cemal', 'cemal'), ('hpla', 'hpla'), ('o-hydroxybenz', 'o-hydroxybenz'), ('htyr', 'htyr'), ('methylbenz', 'methylbenz'), ('vinylcinnamoyl', 'vinylcinnamoyl'), ('2-etmalonamyl', '2-etmalonamyl'), ('asn', 'asn'), ('glu', 'glu'), ('NH2', 'NH2'), ('isobut', 'isobut'), ('2aminopent', '2aminopent'), ('3cl-tyr', '3cl-tyr'), ('heronamide-1', 'heronamide-1'), ('bmt', 'bmt'), ('dap', 'dap'), ('d-met', 'd-met'), ('alpha-OH-phe', 'alpha-OH-phe'), ('AAnon', 'AAnon'), ('trans-1,2-CPDA', 'trans-1,2-CPDA'), ('lipopep-8D1-1', 'lipopep-8D1-1'), ('ile', 'ile'), ('ema', 'ema'), ('dhb', 'dhb'), ('butylguanidine', 'butylguanidine'), ('mmal', 'mmal'), ('d-ile', 'd-ile'), ('mal', 'mal'), ('guan', 'guan'), ('alpha-OH-htyr', 'alpha-OH-htyr'), ('me-tyr', 'me-tyr'), ('gln', 'gln'), ('isoval', 'isoval'), ('val', 'val'), ('DHCHene', 'DHCHene'), ('methylbenz-val', 'methylbenz-val'), ('beta-amino-glu', 'beta-amino-glu'), ('cyclopentene', 'cyclopentene'), ('d-leu', 'd-leu'), ('pyr', 'pyr'), ('16C-FA', '16C-FA'), ('me-glu', 'me-glu'), ('prop', 'prop'), ('14C-FA', '14C-FA'), ('Acetyl-CoA', 'Acetyl-CoA'), ('d-gln', 'd-gln'), ('3measp', '3measp'), ('d-pro', 'd-pro'), ('fatty_acid', 'fatty_acid'), ('end', 'end'), ('ala', 'ala'), ('beta-amino-phe', 'beta-amino-phe'), ('2356-OH-me-benz', '2356-OH-me-benz'), ('d-ser', 'd-ser'), ('mxmal', 'mxmal'), ('piperazic', 'piperazic'), ('d-cys', 'd-cys'), ('m-tyr', 'm-tyr'), ('d-phe', 'd-phe'), ('lys', 'lys'), ('d-val', 'd-val'), ('arg-AA', 'arg-AA'), ('dpg', 'dpg'), ('PNBA', 'PNBA'), ('choi', 'choi'), ('d-asn', 'd-asn'), ('beta-OH-tyr', 'beta-OH-tyr'), ('met', 'met'), ('arg', 'arg'), ('thr', 'thr'), ('d-ala', 'd-ala'), ('gamma-OH-lys', 'gamma-OH-lys'), ('me-PABA', 'me-PABA'), ('d-glu', 'd-glu'), ('DCP', 'DCP'), ('2metbut', '2metbut'), ('orn', 'orn'), ('his', 'his'), ('asp-2', 'asp-2'), ('kyn', 'kyn'), ('shikimic_acid', 'shikimic_acid'), ('3aminobut', '3aminobut'), ('cin', 'cin'), ('trp', 'trp'), ('me-pro', 'me-pro'), ('phe', 'phe'), ('N-OH-orn', 'N-OH-orn'), ('10C-FA', '10C-FA'), ('CHC-CoA', 'CHC-CoA'), ('pip', 'pip'), ('hse', 'hse'), ('beta-OH-asp', 'beta-OH-asp'), ('d-his', 'd-his'), ('d-thr', 'd-thr'), ('me-asp', 'me-asp'), ('plac', 'plac'), ('DHCH', 'DHCH'), ('N/A', 'N/A'), ('aba', 'aba'), ('tyr', 'tyr'), ('6-me-hexyl-thr', '6-me-hexyl-thr'), ('dab', 'dab')], default=None, max_length=20),
        ),
        migrations.AlterField(
            model_name='at',
            name='substrate',
            field=models.CharField(choices=[('a3abut', 'a3abut'), ('mthz', 'mthz'), ('butmal', 'butmal'), ('leu', 'leu'), ('8C-AA', '8C-AA'), ('d-arg', 'd-arg'), ('benz', 'benz'), ('d-lys', 'd-lys'), ('be-14106-1', 'be-14106-1'), ('butylamine', 'butylamine'), ('cremimycin1', 'cremimycin1'), ('pro', 'pro'), ('PABA', 'PABA'), ('propylamine', 'propylamine'), ('d-glu-2', 'd-glu-2'), ('ml-449-1', 'ml-449-1'), ('asp', 'asp'), ('gly', 'gly'), ('cys', 'cys'), ('isobutmal', 'isobutmal'), ('AHBA', 'AHBA'), ('2-oxobutmal', '2-oxobutmal'), ('d-asp', 'd-asp'), ('mxmal_ACP', 'mxmal_ACP'), ('mpro', 'mpro'), ('ser', 'ser'), ('beta-OH-asn', 'beta-OH-asn'), ('hpg', 'hpg'), ('ethylguanidine', 'ethylguanidine'), ('d-trp', 'd-trp'), ('d-tyr', 'd-tyr'), ('cemal', 'cemal'), ('hpla', 'hpla'), ('3-me-hexmal', '3-me-hexmal'), ('o-hydroxybenz', 'o-hydroxybenz'), ('htyr', 'htyr'), ('methylbenz', 'methylbenz'), ('vinylcinnamoyl', 'vinylcinnamoyl'), ('2-etmalonamyl', '2-etmalonamyl'), ('asn', 'asn'), ('glu', 'glu'), ('NH2', 'NH2'), ('isobut', 'isobut'), ('2aminopent', '2aminopent'), ('3cl-tyr', '3cl-tyr'), ('heronamide-1', 'heronamide-1'), ('bmt', 'bmt'), ('dap', 'dap'), ('d-met', 'd-met'), ('alpha-OH-phe', 'alpha-OH-phe'), ('emal', 'emal'), ('AAnon', 'AAnon'), ('trans-1,2-CPDA', 'trans-1,2-CPDA'), ('ile', 'ile'), ('lipopep-8D1-1', 'lipopep-8D1-1'), ('dhb', 'dhb'), ('ema', 'ema'), ('butylguanidine', 'butylguanidine'), ('mmal', 'mmal'), ('d-ile', 'd-ile'), ('mal', 'mal'), ('guan', 'guan'), ('alpha-OH-htyr', 'alpha-OH-htyr'), ('me-tyr', 'me-tyr'), ('gln', 'gln'), ('isoval', 'isoval'), ('val', 'val'), ('DHCHene', 'DHCHene'), ('allylmal', 'allylmal'), ('methylbenz-val', 'methylbenz-val'), ('beta-amino-glu', 'beta-amino-glu'), ('cyclopentene', 'cyclopentene'), ('d-leu', 'd-leu'), ('pyr', 'pyr'), ('16C-FA', '16C-FA'), ('me-glu', 'me-glu'), ('prop', 'prop'), ('14C-FA', '14C-FA'), ('d-gln', 'd-gln'), ('Acetyl-CoA', 'Acetyl-CoA'), ('3measp', '3measp'), ('d-pro', 'd-pro'), ('end', 'end'), ('fatty_acid', 'fatty_acid'), ('ala', 'ala'), ('beta-amino-phe', 'beta-amino-phe'), ('2356-OH-me-benz', '2356-OH-me-benz'), ('d-ser', 'd-ser'), ('mxmal', 'mxmal'), ('hexmal', 'hexmal'), ('piperazic', 'piperazic'), ('d-cys', 'd-cys'), ('m-tyr', 'm-tyr'), ('d-phe', 'd-phe'), ('lys', 'lys'), ('d-val', 'd-val'), ('arg-AA', 'arg-AA'), ('dpg', 'dpg'), ('choi', 'choi'), ('PNBA', 'PNBA'), ('d-asn', 'd-asn'), ('beta-OH-tyr', 'beta-OH-tyr'), ('met', 'met'), ('arg', 'arg'), ('thr', 'thr'), ('d-ala', 'd-ala'), ('gamma-OH-lys', 'gamma-OH-lys'), ('me-PABA', 'me-PABA'), ('d-glu', 'd-glu'), ('DCP', 'DCP'), ('2metbut', '2metbut'), ('orn', 'orn'), ('his', 'his'), ('asp-2', 'asp-2'), ('kyn', 'kyn'), ('shikimic_acid', 'shikimic_acid'), ('3aminobut', '3aminobut'), ('trp', 'trp'), ('cin', 'cin'), ('me-pro', 'me-pro'), ('phe', 'phe'), ('N-OH-orn', 'N-OH-orn'), ('10C-FA', '10C-FA'), ('CHC-CoA', 'CHC-CoA'), ('pip', 'pip'), ('hse', 'hse'), ('beta-OH-asp', 'beta-OH-asp'), ('d-his', 'd-his'), ('D-isobutmal', 'D-isobutmal'), ('d-thr', 'd-thr'), ('me-asp', 'me-asp'), ('plac', 'plac'), ('DHCH', 'DHCH'), ('hmal', 'hmal'), ('N/A', 'N/A'), ('aba', 'aba'), ('tyr', 'tyr'), ('6-me-hexyl-thr', '6-me-hexyl-thr'), ('dab', 'dab')], default='mal', max_length=20),
        ),
        migrations.AlterField(
            model_name='cal',
            name='substrate',
            field=models.CharField(choices=[('a3abut', 'a3abut'), ('mthz', 'mthz'), ('butmal', 'butmal'), ('leu', 'leu'), ('8C-AA', '8C-AA'), ('d-arg', 'd-arg'), ('benz', 'benz'), ('d-lys', 'd-lys'), ('be-14106-1', 'be-14106-1'), ('butylamine', 'butylamine'), ('cremimycin1', 'cremimycin1'), ('pro', 'pro'), ('PABA', 'PABA'), ('propylamine', 'propylamine'), ('d-glu-2', 'd-glu-2'), ('ml-449-1', 'ml-449-1'), ('asp', 'asp'), ('gly', 'gly'), ('cys', 'cys'), ('isobutmal', 'isobutmal'), ('AHBA', 'AHBA'), ('2-oxobutmal', '2-oxobutmal'), ('d-asp', 'd-asp'), ('mxmal_ACP', 'mxmal_ACP'), ('mpro', 'mpro'), ('ser', 'ser'), ('beta-OH-asn', 'beta-OH-asn'), ('hpg', 'hpg'), ('ethylguanidine', 'ethylguanidine'), ('d-trp', 'd-trp'), ('d-tyr', 'd-tyr'), ('cemal', 'cemal'), ('hpla', 'hpla'), ('3-me-hexmal', '3-me-hexmal'), ('o-hydroxybenz', 'o-hydroxybenz'), ('htyr', 'htyr'), ('methylbenz', 'methylbenz'), ('vinylcinnamoyl', 'vinylcinnamoyl'), ('2-etmalonamyl', '2-etmalonamyl'), ('asn', 'asn'), ('glu', 'glu'), ('NH2', 'NH2'), ('isobut', 'isobut'), ('2aminopent', '2aminopent'), ('3cl-tyr', '3cl-tyr'), ('heronamide-1', 'heronamide-1'), ('bmt', 'bmt'), ('dap', 'dap'), ('d-met', 'd-met'), ('alpha-OH-phe', 'alpha-OH-phe'), ('emal', 'emal'), ('AAnon', 'AAnon'), ('trans-1,2-CPDA', 'trans-1,2-CPDA'), ('ile', 'ile'), ('lipopep-8D1-1', 'lipopep-8D1-1'), ('dhb', 'dhb'), ('ema', 'ema'), ('butylguanidine', 'butylguanidine'), ('mmal', 'mmal'), ('d-ile', 'd-ile'), ('mal', 'mal'), ('guan', 'guan'), ('alpha-OH-htyr', 'alpha-OH-htyr'), ('me-tyr', 'me-tyr'), ('gln', 'gln'), ('isoval', 'isoval'), ('val', 'val'), ('DHCHene', 'DHCHene'), ('allylmal', 'allylmal'), ('methylbenz-val', 'methylbenz-val'), ('beta-amino-glu', 'beta-amino-glu'), ('cyclopentene', 'cyclopentene'), ('d-leu', 'd-leu'), ('pyr', 'pyr'), ('16C-FA', '16C-FA'), ('me-glu', 'me-glu'), ('prop', 'prop'), ('14C-FA', '14C-FA'), ('d-gln', 'd-gln'), ('Acetyl-CoA', 'Acetyl-CoA'), ('3measp', '3measp'), ('d-pro', 'd-pro'), ('end', 'end'), ('fatty_acid', 'fatty_acid'), ('ala', 'ala'), ('beta-amino-phe', 'beta-amino-phe'), ('2356-OH-me-benz', '2356-OH-me-benz'), ('d-ser', 'd-ser'), ('mxmal', 'mxmal'), ('hexmal', 'hexmal'), ('piperazic', 'piperazic'), ('d-cys', 'd-cys'), ('m-tyr', 'm-tyr'), ('d-phe', 'd-phe'), ('lys', 'lys'), ('d-val', 'd-val'), ('arg-AA', 'arg-AA'), ('dpg', 'dpg'), ('choi', 'choi'), ('PNBA', 'PNBA'), ('d-asn', 'd-asn'), ('beta-OH-tyr', 'beta-OH-tyr'), ('met', 'met'), ('arg', 'arg'), ('thr', 'thr'), ('d-ala', 'd-ala'), ('gamma-OH-lys', 'gamma-OH-lys'), ('me-PABA', 'me-PABA'), ('d-glu', 'd-glu'), ('DCP', 'DCP'), ('2metbut', '2metbut'), ('orn', 'orn'), ('his', 'his'), ('asp-2', 'asp-2'), ('kyn', 'kyn'), ('shikimic_acid', 'shikimic_acid'), ('3aminobut', '3aminobut'), ('trp', 'trp'), ('cin', 'cin'), ('me-pro', 'me-pro'), ('phe', 'phe'), ('N-OH-orn', 'N-OH-orn'), ('10C-FA', '10C-FA'), ('CHC-CoA', 'CHC-CoA'), ('pip', 'pip'), ('hse', 'hse'), ('beta-OH-asp', 'beta-OH-asp'), ('d-his', 'd-his'), ('D-isobutmal', 'D-isobutmal'), ('d-thr', 'd-thr'), ('me-asp', 'me-asp'), ('plac', 'plac'), ('DHCH', 'DHCH'), ('hmal', 'hmal'), ('N/A', 'N/A'), ('aba', 'aba'), ('tyr', 'tyr'), ('6-me-hexyl-thr', '6-me-hexyl-thr'), ('dab', 'dab')], default='mal', max_length=20),
        ),
    ]