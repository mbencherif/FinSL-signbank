# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError, DataError
from django.db import transaction

from signbank.dictionary.models import (Gloss, Dataset, SignLanguage, Language, Keyword, Translation, Definition,
                                        Dialect, RelationToForeignSign, FieldChoice, MorphologyDefinition)
from signbank.dictionary.models import build_choice_list


class GlossTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", email=None, password=None)
        # Migrations have id=1 already
        self.language = Language.objects.create(name="glang", language_code_2char="gl", language_code_3char="gla")
        self.signlanguage = SignLanguage.objects.create(pk=2, name="testsignlanguage", language_code_3char="tst")
        self.dataset = Dataset.objects.create(name="testdataset", signlanguage=self.signlanguage)
        self.gloss = Gloss.objects.create(idgloss="testgloss", dataset=self.dataset, created_by=self.user,
                                          updated_by=self.user)

    def test_str(self):
        self.assertEqual(unicode(self.gloss), self.gloss.idgloss)

    def test_locked(self):
        """Test that locking Gloss works."""
        gloss = Gloss.objects.get(idgloss="testgloss")
        # Should be locked when first created
        self.assertFalse(gloss.locked)

        # Set locked True, and check that the Gloss is locked.
        gloss.locked = True
        gloss.save()
        self.assertTrue(gloss.locked)

    def test_unique_together(self):
        """Make sure that there can't be two of the same gloss+dataset combinations"""
        gloss = Gloss.objects.get(idgloss="testgloss")

        # Create another Gloss
        new_gloss = Gloss.objects.create(idgloss="testgloss2", dataset=self.dataset, created_by=self.user,
                                         updated_by=self.user)
        new_dataset = Dataset.objects.create(name="testdataset2", signlanguage=self.signlanguage)
        self.assertEqual(new_gloss.idgloss, "testgloss2")

        # Make sure you cannot violate unique_together by changing the Gloss.idgloss
        with self.assertRaises(IntegrityError):  # Should return IntegrityError
            with transaction.atomic():
                new_gloss.idgloss = "testgloss"
                new_gloss.save()

        # Change to a new dataset
        new_gloss.dataset = new_dataset
        new_gloss.save()
        self.assertTrue(new_gloss.dataset == new_dataset)

        # Change new_gloss to the same as gloss
        new_gloss.idgloss = "testgloss"
        new_gloss.save()
        self.assertTrue(new_gloss.idgloss == gloss.idgloss)

        # Make sure that you cannot violate unique_together by changing Dataset
        with self.assertRaises(IntegrityError):  # Should return IntegrityError
            with transaction.atomic():
                gloss.dataset = new_dataset
                gloss.save()

    def test_idgloss(self):
        """Tests idgloss"""
        gloss = Gloss.objects.get(idgloss="testgloss")

        # Check for some weird characters
        weird_chars = ("äöåÄÖÅ¨^~'* ´`üÜÿŸëêËÊ€$#", "ЁЂЃЄЅІЇЌЍЎЏАБВДЖИКОПРСТФХЦЧЩЫ", "؟ الستارود أي بعد, معاملة بيو",)
        for my_str in weird_chars:
            gloss.idgloss = my_str
            gloss.save()
            self.assertEqual(gloss.idgloss, str(gloss.idgloss))
            self.assertEqual(gloss.idgloss, my_str)

        # Test that the length of idgloss can't be too long
        with self.assertRaises(DataError):
            gloss.idgloss = "afasdkfjsdalkfjdsaljfl^¨'*´`} sajfljadsklfjasdklfjsadkjflÄÖÅlöjsadkfjasdkljflaksdjfkljds"
            "fljasdlkfjakdslkafjsdlkafjölasdjfkldsajlaköfjsdakljfklasdjfkldsjaflkajdsflökjdsalkfjadslköfjdsalökjfklsd"
            "ajflkdsjlkfajöldskjflkadsjflkdsajfladslkfjdlksa"
            gloss.save()

    def test_idgloss_dataset(self):
        """Test that a Gloss cannot be created without a relation to Dataset."""
        with self.assertRaises(IntegrityError):
            Gloss.objects.create(idgloss="testgloss7", created_by=self.user, updated_by=self.user)

    def test_idgloss_en(self):
        """Tests the field idgloss_en."""
        # Check that the max_length can't be exceeded.
        with self.assertRaises(DataError):
            en = Gloss.objects.create(idgloss="testgloss_en", idgloss_en="äöå1@r" * 10 + "1", dataset=self.dataset,
                                      created_by=self.user, updated_by=self.user)

    def test_created_by(self):
        """Tests that the created_by field functions when a gloss is created."""
        gl = Gloss.objects.create(idgloss="testgloss_createdby", dataset=self.dataset,
                                  created_by=self.user, updated_by=self.user)
        self.assertEqual(gl.created_by, self.user)

    def test_get_translation_languages(self):
        """Tests function get_translation_languages()"""
        self.dataset.translation_languages = (self.language,)
        self.dataset.save()
        self.assertIn(self.language, Gloss.get_translation_languages(self.gloss))

    def test_get_translations_for_translation_languages(self):
        """Test function get_translations_for_translation_languages()"""
        keyword = Keyword.objects.create(text="akeyword")
        keyword2 = Keyword.objects.create(text="another")
        translation = Translation.objects.create(gloss=self.gloss, language=self.language, keyword=keyword,
                                                      index=2)
        translation2 = Translation.objects.create(gloss=self.gloss, language=self.language, keyword=keyword2, index=3)
        self.dataset.translation_languages = (self.language,)
        self.dataset.save()
        unzip = zip(*Gloss.get_translations_for_translation_languages(self.gloss))
        languages, translations = unzip[0], unzip[1]

        self.assertIn(self.language, languages)
        self.assertTrue(all(x in (translation, translation2) for x in list(*translations)))

    def test_field_labels(self):
        """Test that function returns proper field labels."""
        meta_fields = self.gloss._meta.fields
        field_names = dict()
        for field in meta_fields:
            field_names[field.name] = field.verbose_name
        self.assertDictEqual(Gloss.field_labels(self.gloss), field_names)

    def test_get_fields(self):
        """Test function."""
        field_list = []
        for field in Gloss._meta.fields:
            field_list.append((field.name, field.value_to_string(self.gloss)))
        self.assertListEqual(Gloss.get_fields(self.gloss), field_list)


class DatasetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testdata", email=None, password=None)
        # Migrations have id=1 already
        self.signlanguage = SignLanguage.objects.create(pk=3, name="slang", language_code_3char="tst")
        self.dataset = Dataset.objects.create(name="dataset", signlanguage=self.signlanguage)

    def test_str(self):
        """Test unicode string representation."""
        self.assertEqual(unicode(self.dataset), self.dataset.name)


class TranslationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testtrans", email=None, password=None)
        self.language = Language.objects.create(name="mylang", language_code_2char="ml", language_code_3char="myl")
        # Migrations have id=1 already for a SignLanguage
        self.signlanguage = SignLanguage.objects.create(pk=4, name="signlang", language_code_3char="sla")
        self.dataset = Dataset.objects.create(name="dataset", signlanguage=self.signlanguage)
        self.gloss = Gloss.objects.create(idgloss="transgloss", dataset=self.dataset, created_by=self.user,
                                          updated_by=self.user)
        self.keyword = Keyword.objects.create(text="myword")
        # Create a Translation
        self.translation = Translation.objects.create(gloss=self.gloss, language=self.language, keyword=self.keyword,
                                                      index=1)

    def test_str(self):
        """Test unicode string representation."""
        self.assertEqual(unicode(self.translation), self.gloss.idgloss + '-' + self.keyword.text)


class KeywordTestCase(TestCase):
    def setUp(self):
        self.keyword = Keyword.objects.create(text="mykeyworD")

    def test_str(self):
        self.assertEqual(unicode(self.keyword), self.keyword.text)


class DefinitionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testdef", email=None, password=None)
        self.signlanguage = SignLanguage.objects.create(pk=4, name="signl", language_code_3char="sla")
        self.dataset = Dataset.objects.create(name="dataset2", signlanguage=self.signlanguage)
        self.gloss = Gloss.objects.create(idgloss="defgloss", dataset=self.dataset, created_by=self.user,
                                          updated_by=self.user)
        self.definition = Definition.objects.create(gloss=self.gloss, text="test text tööt", role="note", count=10)

    def test_str(self):
        self.assertEqual(unicode(self.definition), self.gloss.idgloss + "/" + self.definition.role)


class LanguageTestCase(TestCase):
    def setUp(self):
        self.language = Language.objects.create(name=u"New ÖÄ Language", language_code_2char="nl",
                                                language_code_3char="nla", description="New language we just created")

    def test_str(self):
        self.assertEqual(unicode(self.language), self.language.name)


class DialectTestCase(TestCase):
    def setUp(self):
        self.signlanguage = SignLanguage.objects.create(pk=5, name=u"sÄÄö", language_code_3char="ÄÄö")
        self.dialect = Dialect.objects.create(language=self.signlanguage, name=u"Northern sÄÄö",
                                              description=u"Northern sÄÄö has traditionally been used in the North "
                                                          u"Pole, But to this day it has also spread to Greenland.")

    def test_str(self):
        self.assertEqual(unicode(self.dialect), self.signlanguage.name + "/" + self.dialect.name)


class RelationToForeignSignTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testrel", email=None, password=None)
        self.signlanguage = SignLanguage.objects.create(pk=6, name="lala", language_code_3char="lal")
        self.dataset = Dataset.objects.create(name="relset", signlanguage=self.signlanguage)
        self.gloss = Gloss.objects.create(idgloss="related-GLOSS", dataset=self.dataset, created_by=self.user,
                                          updated_by=self.user)
        self.relation = RelationToForeignSign.objects.create(gloss=self.gloss, loan=True, other_lang=u"sÄÄö",
                                                             other_lang_gloss="Samp-GLOSS")

    def test_str(self):
        self.assertEqual(unicode(self.relation), self.gloss.idgloss + "/" + self.relation.other_lang + "," +
                         self.relation.other_lang_gloss)


class FieldChoiceTestCase(TestCase):
    def setUp(self):
        self.fieldchoice = FieldChoice.objects.create(field="field", english_name="mychoice", machine_value=1)

    def test_str(self):
        self.assertEqual(unicode(self.fieldchoice), self.fieldchoice.english_name)


class MorphologyDefinitionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="usermorph", email=None, password=None)
        self.signlanguage = SignLanguage.objects.create(pk=11, name="definitive", language_code_3char="def")
        self.dataset = Dataset.objects.create(name="morphdata", signlanguage=self.signlanguage)
        self.gloss = Gloss.objects.create(idgloss="morhp-gloss", dataset=self.dataset, created_by=self.user,
                                          updated_by=self.user)
        self.gloss2 = Gloss.objects.create(idgloss="morhp-gloss2", dataset=self.dataset, created_by=self.user,
                                           updated_by=self.user)
        self.fieldchoice = FieldChoice.objects.create(field="newfield", english_name="nice name", machine_value=2)
        self.morphdef = MorphologyDefinition.objects.create(parent_gloss=self.gloss, morpheme=self.gloss2,
                                                            role=self.fieldchoice)

    def test_str(self):
        self.assertEqual(unicode(self.morphdef), self.morphdef.morpheme.idgloss + " is " +
                         self.morphdef.role.english_name + " of " + self.morphdef.parent_gloss.idgloss)


class FunctionsTestCase(TestCase):
    def setUp(self):
        self.field = "testField"
        f1 = FieldChoice.objects.create(field=self.field, english_name="choice1", machine_value=1)
        f2 = FieldChoice.objects.create(field=self.field, english_name="choice_another", machine_value=2)
        f3 = FieldChoice.objects.create(field=self.field, english_name="full-of-choices", machine_value=3)
        self.choices = []
        self.choices.append((str(f1.machine_value), unicode(f1)))
        self.choices.append((str(f2.machine_value), unicode(f2)))
        self.choices.append((str(f3.machine_value), unicode(f3)))

    def test_build_choice_list(self):
        """Test that function returns proper values."""
        # TODO: Simulate OperationalError?
        self.assertListEqual(build_choice_list(self.field), self.choices)

