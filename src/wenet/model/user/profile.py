from __future__ import absolute_import, annotations

import re
from numbers import Number
from typing import List, Optional, Dict

from wenet.model.scope import AbstractScopeMappings, Scope
from wenet.model.user.common import Gender, Date
from wenet.model.norm import Norm
from babel.core import Locale


class CoreWeNetUserProfile:

    class ScopeMappings(AbstractScopeMappings):
        @staticmethod
        def _get_mappings() -> Dict[Scope, str]:
            return {
                Scope.ID: "id",
                Scope.BIRTHDATE: "dateOfBirth",
                Scope.GENDER: "gender",
                Scope.NATIONALITY: "nationality",
                Scope.LOCALE: "locale",
                Scope.PHONE_NUMBER: "phoneNumber",
                Scope.EMAIL: "email",
            }

    def __init__(self,
                 name: Optional[UserName],
                 date_of_birth: Optional[Date],
                 gender: Optional[Gender],
                 email: Optional[str],
                 phone_number: Optional[str],
                 locale: Optional[str],
                 avatar: Optional[str],
                 nationality: Optional[str],
                 #languages: Optional[List[UserLanguage]],
                 occupation: Optional[str],
                 creation_ts: Optional[Number],
                 last_update_ts: Optional[Number],
                 profile_id: Optional[str],
                 ):
        self.name = name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.email = email
        self.phone_number = phone_number
        self.locale = locale
        self.avatar = avatar
        self.nationality = nationality
        # self.languages = languages
        self.occupation = occupation
        self.creation_ts = creation_ts
        self.last_update_ts = last_update_ts
        self.profile_id = profile_id

        if name:
            if not isinstance(name, UserName):
                raise TypeError("Name should be a UserName object")
        else:
            self.name = UserName(
                first=None,
                middle=None,
                last=None,
                prefix=None,
                suffix=None
            )
        if date_of_birth:
            if not isinstance(date_of_birth, Date):
                raise TypeError("Date of birth should be a Date")
        if gender:
            if not isinstance(gender, Gender):
                raise TypeError("Gender should be a Gender object")
        if email:
            if not isinstance(email, str):
                raise TypeError("Email should be a string")
            if not self.is_valid_mail(email):
                raise ValueError("[%s] is not a valid email" % email)
        if phone_number:
            if not isinstance(phone_number, str):
                raise TypeError("Phone number should be a string")
        if locale:
            if not isinstance(locale, str):
                raise TypeError("Locale should be a string")
            if not self.is_valid_locale(locale):
                raise ValueError("[%s] is not a valid Locale" % locale)
        if avatar:
            if not isinstance(avatar, str):
                raise TypeError("Avatar should be a string")
        if nationality:
            if not isinstance(nationality, str):
                raise TypeError("Nationality should be a string")

        # if languages:
        #     if not isinstance(languages, list):
        #         raise TypeError("Languages should be list of UserLanguage")
        #     else:
        #         for language in languages:
        #             if not isinstance(language, UserLanguage):
        #                 raise TypeError("Languages should be list of UserLanguage")
        else:
            self.languages = []
        if occupation:
            if not isinstance(occupation, str):
                raise TypeError("Occupation should be a string")

        if creation_ts:
            if not isinstance(creation_ts, Number):
                raise TypeError("CreationTs should be a Number")
        if last_update_ts:
            if not isinstance(last_update_ts, Number):
                raise TypeError("LastUpdateTs should be a Number")

        if profile_id:
            if not isinstance(profile_id, str):
                raise TypeError("Profile id should be a string")

    def to_repr(self) -> dict:
        return {
            "name": self.name.to_repr() if self.name is not None else None,
            "dateOfBirth": self.date_of_birth.to_repr() if self.date_of_birth is not None else None,
            "gender": self.gender.value if self.gender else None,
            "email": self.email,
            "phoneNumber": self.phone_number,
            "locale": self.locale,
            "avatar": self.avatar,
            "nationality": self.nationality,
            "occupation": self.occupation,
            "_creationTs": self.creation_ts,
            "_lastUpdateTs": self.last_update_ts,
            "id": str(self.profile_id),
        }

    def to_filtered_repr(self, scope_list: List[Scope]) -> dict:
        profile_repr = self.to_repr()

        result = {
            "name": self.name.to_filtered_repr(scope_list) if self.name is not None else None
        }

        for scope in scope_list:
            field = self.ScopeMappings.get_field(scope)
            if field is not None:
                result[field] = profile_repr[field]

        return result

    def to_public_repr(self) -> dict:
        scopes = [
            Scope.ID,
            Scope.FIRST_NAME,
            Scope.LAST_NAME
        ]

        return self.to_filtered_repr(scopes)

    @staticmethod
    def from_repr(raw_data: dict, profile_id: Optional[str] = None) -> CoreWeNetUserProfile:
        if profile_id is None:
            profile_id = raw_data.get("id")

        return CoreWeNetUserProfile(
            name=UserName.from_repr(raw_data["name"]) if raw_data.get("name") is not None else None,
            date_of_birth=Date.from_repr(raw_data["dateOfBirth"]) if raw_data.get("dateOfBirth") is not None else None,
            gender=Gender(raw_data["gender"]) if raw_data.get("gender", None) else None,
            email=raw_data.get("email", None),
            phone_number=raw_data.get("phoneNumber", None),
            locale=raw_data.get("locale", None),
            avatar=raw_data.get("avatar", None),
            nationality=raw_data.get("nationality", None),
            occupation=raw_data.get("occupation", None),
            creation_ts=raw_data.get("_creationTs", None),
            last_update_ts=raw_data.get("_lastUpdateTs", None),
            profile_id=profile_id
        )

    def update(self, other: CoreWeNetUserProfile) -> CoreWeNetUserProfile:
        self.profile_id = other.profile_id
        self.name = other.name
        self.date_of_birth = other.date_of_birth
        self.gender = other.gender
        self.email = other.email
        self.phone_number = other.phone_number
        self.locale = other.locale
        self.avatar = other.avatar
        self.nationality = other.nationality
        self.occupation = other.occupation
        self.creation_ts = other.creation_ts
        self.last_update_ts = other.last_update_ts

        return self

    @staticmethod
    def is_valid_mail(mail: str):
        reg_exp = r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w+)+$"
        return re.search(reg_exp, mail)

    @staticmethod
    def is_valid_locale(locale: str) -> bool:
        try:
            Locale.parse(locale)
            return True
        except ValueError:
            return False

    def __repr__(self):
        return str(self.to_repr())

    def __str__(self):
        return self.__repr__()

    def __eq__(self, o) -> bool:
        if not isinstance(o, CoreWeNetUserProfile):
            return False
        return self.name == o.name and self.date_of_birth == o.date_of_birth and self.gender == o.gender and self.email == o.email \
            and self.phone_number == o.phone_number and self.locale == o.locale and self.avatar == o.avatar and self.nationality == o.nationality \
            and self.occupation == o.occupation and self.creation_ts == o.creation_ts and self.last_update_ts == o.last_update_ts \
            and self.profile_id == o.profile_id

    @staticmethod
    def empty(wenet_user_id: str) -> CoreWeNetUserProfile:
        return CoreWeNetUserProfile(
            name=UserName.empty(),
            date_of_birth=Date.empty(),
            gender=None,
            email=None,
            phone_number=None,
            locale=None,
            avatar=None,
            nationality=None,
            occupation=None,
            creation_ts=None,
            last_update_ts=None,
            profile_id=wenet_user_id
        )


class WeNetUserProfile(CoreWeNetUserProfile):

    def __init__(self,
                 name: Optional[UserName],
                 date_of_birth: Optional[Date],
                 gender: Optional[Gender],
                 email: Optional[str],
                 phone_number: Optional[str],
                 locale: Optional[str],
                 avatar: Optional[str],
                 nationality: Optional[str],
                 occupation: Optional[str],
                 creation_ts: Optional[Number],
                 last_update_ts: Optional[Number],
                 profile_id: Optional[str],
                 norms: Optional[List[Norm]],
                 planned_activities: Optional[list],
                 relevant_locations: Optional[list],
                 relationships: Optional[list],
                 personal_behaviours: Optional[list],
                 materials: Optional[list],
                 competences: Optional[list],
                 meanings: Optional[list]
                 ):

        super().__init__(
            name=name,
            date_of_birth=date_of_birth,
            gender=gender,
            email=email,
            phone_number=phone_number,
            locale=locale,
            avatar=avatar,
            nationality=nationality,
            occupation=occupation,
            creation_ts=creation_ts,
            last_update_ts=last_update_ts,
            profile_id=profile_id
        )
        self.norms = norms
        self.planned_activities = planned_activities
        self.relevant_locations = relevant_locations
        self.relationships = relationships
        self.personal_behaviours = personal_behaviours
        self.materials = materials
        self.competences = competences
        self.meanings = meanings

        if norms:
            if not isinstance(norms, list):
                raise TypeError("Norms should be a list of norms")
            else:
                for norm in norms:
                    if not isinstance(norm, Norm):
                        raise TypeError("Norms should be a list of norms")
        else:
            self.norms = []

        if materials:
            if not isinstance(materials, list):
                raise TypeError("Materials should be a list")
        else:
            self.materials = []

        if competences:
            if not isinstance(competences, list):
                raise TypeError("Competences should be a list")
        else:
            self.competences = []

        if meanings:
            if not isinstance(meanings, list):
                raise TypeError("Meanings should be a list")
        else:
            self.meanings = []

        if planned_activities:
            if not isinstance(planned_activities, list):
                raise TypeError("PlannedActivities should be a list")
        else:
            self.planned_activities = []

        if relevant_locations:
            if not isinstance(relevant_locations, list):
                raise TypeError("RelevantLocations should be a list")
        else:
            self.relevant_locations = []

        if relationships:
            if not isinstance(relationships, list):
                raise TypeError("Relationship should be a list")
        else:
            self.relationships = []

        if personal_behaviours:
            if not isinstance(personal_behaviours, list):
                raise TypeError("personalBehaviors should be a list")
        else:
            self.personal_behaviours = []

    def to_repr(self) -> dict:
        base_repr = super().to_repr()
        base_repr.update({
            "norms": list(x.to_repr() for x in self.norms),
            "plannedActivities": self.planned_activities,
            "relevantLocations": self.relevant_locations,
            "relationships": self.relationships,
            "personalBehaviors": self.personal_behaviours,
            "materials": self.materials,
            "competences": self.competences,
            "meanings": self.meanings
        })

        return base_repr

    @staticmethod
    def from_repr(raw_data: dict, profile_id: Optional[str] = None) -> WeNetUserProfile:

        if profile_id is None:
            profile_id = raw_data.get("id")

        return WeNetUserProfile(
            name=UserName.from_repr(raw_data["name"]) if raw_data.get("name") is not None else None,
            date_of_birth=Date.from_repr(raw_data["dateOfBirth"]) if raw_data.get("dateOfBirth") is not None else None,
            gender=Gender(raw_data["gender"]) if raw_data.get("gender", None) else None,
            email=raw_data.get("email", None),
            phone_number=raw_data.get("phoneNumber", None),
            locale=raw_data.get("locale", None),
            avatar=raw_data.get("avatar", None),
            nationality=raw_data.get("nationality", None),
            occupation=raw_data.get("occupation", None),
            creation_ts=raw_data.get("_creationTs", None),
            last_update_ts=raw_data.get("_lastUpdateTs", None),
            profile_id=profile_id,
            norms=list(Norm.from_repr(x) for x in raw_data["norms"]) if raw_data.get("norms", None) else None,
            planned_activities=raw_data.get("plannedActivities", None),
            relevant_locations=raw_data.get("relevantLocations", None),
            relationships=raw_data.get("relationships", None),
            personal_behaviours=raw_data.get("personalBehaviors", None),
            materials=raw_data.get("materials", None),
            competences=raw_data.get("competences", None),
            meanings=raw_data.get("meanings", None)
        )

    def update(self, other: CoreWeNetUserProfile) -> WeNetUserProfile:

        super().update(other)

        if isinstance(other, WeNetUserProfile):
            self.norms = other.norms
            self.planned_activities = other.planned_activities
            self.relevant_locations = other.relevant_locations
            self.relationships = other.relationships
            self.personal_behaviours = other.personal_behaviours
            self.materials = other.materials
            self.competences = other.competences
            self.meanings = other.meanings

        return self

    def __repr__(self):
        return str(self.to_repr())

    def __str__(self):
        return self.__repr__()

    def __eq__(self, o):
        if not isinstance(o, WeNetUserProfile):
            return False
        return super().__eq__(o) and self.norms == o.norms and self.planned_activities == o.planned_activities and self.relevant_locations == o.relationships \
            and self.relationships == o.relationships and self.personal_behaviours == o.personal_behaviours and self.materials == o.materials \
            and self.competences == o.competences and self.meanings == o.meanings

    @staticmethod
    def empty(wenet_user_id: str) -> WeNetUserProfile:
        return WeNetUserProfile(
            name=UserName.empty(),
            date_of_birth=Date.empty(),
            gender=None,
            email=None,
            phone_number=None,
            locale=None,
            avatar=None,
            nationality=None,
            occupation=None,
            creation_ts=None,
            last_update_ts=None,
            profile_id=wenet_user_id,
            norms=None,
            planned_activities=None,
            relevant_locations=None,
            relationships=None,
            personal_behaviours=None,
            materials=None,
            competences=None,
            meanings=None
        )

    @staticmethod
    def create_from_core_profile(profile: CoreWeNetUserProfile) -> WeNetUserProfile:
        return WeNetUserProfile(
            name=profile.name,
            date_of_birth=profile.date_of_birth,
            gender=profile.gender,
            email=profile.email,
            phone_number=profile.phone_number,
            locale=profile.locale,
            avatar=profile.avatar,
            nationality=profile.nationality,
            occupation=profile.occupation,
            creation_ts=profile.creation_ts,
            last_update_ts=profile.last_update_ts,
            profile_id=profile.profile_id,
            norms=None,
            planned_activities=None,
            relevant_locations=None,
            relationships=None,
            personal_behaviours=None,
            materials=None,
            competences=None,
            meanings=None
        )


class UserName:

    class ScopeMappings(AbstractScopeMappings):
        @staticmethod
        def _get_mappings() -> Dict[Scope, str]:
            return {
                Scope.FIRST_NAME: "first",
                Scope.MIDDLE_NAME: "middle",
                Scope.LAST_NAME: "last",
                Scope.PREFIX_NAME: "prefix",
                Scope.SUFFIX_NAME: "suffix",
            }

    def __init__(self, first: Optional[str], middle: Optional[str], last: Optional[str], prefix: Optional[str], suffix: Optional[str]):
        self.first = first
        self.middle = middle
        self.last = last
        self.prefix = prefix
        self.suffix = suffix

        if first:
            if not isinstance(first, str):
                raise TypeError("First should be a string")
        if middle:
            if not isinstance(middle, str):
                raise TypeError("Middle should be a string")
        if last:
            if not isinstance(last, str):
                raise TypeError("Last should be a string")
        if prefix:
            if not isinstance(prefix, str):
                raise TypeError("Prefix should be a string")
        if suffix:
            if not isinstance(suffix, str):
                raise TypeError("Suffix should be a string")

    def to_repr(self, public_profile: bool = False) -> dict:
        if public_profile:
            return {
                "first": self.first,
                "last": self.last,
            }
        else:
            return {
                "first": self.first,
                "middle": self.middle,
                "last": self.last,
                "prefix": self.prefix,
                "suffix": self.suffix
            }

    def to_filtered_repr(self, scope_list: List[Scope]) -> dict:
        name_repr = self.to_repr()
        result = {}

        for scope in scope_list:
            field = self.ScopeMappings.get_field(scope)
            if field is not None:
                result[field] = name_repr[field]

        return result

    @staticmethod
    def from_repr(raw_data: dict) -> UserName:
        return UserName(
            first=raw_data.get("first", None),
            middle=raw_data.get("middle", None),
            last=raw_data.get("last", None),
            prefix=raw_data.get("prefix", None),
            suffix=raw_data.get("suffix", None)
        )

    @staticmethod
    def empty() -> UserName:
        return UserName(
            first=None,
            middle=None,
            last=None,
            prefix=None,
            suffix=None
        )

    def __repr__(self):
        return str(self.to_repr())

    def __str__(self):
        return self.__repr__()

    def __eq__(self, o):
        if not isinstance(o, UserName):
            return False
        return self.first == o.first and self.middle == o.middle and self.last == o.last and self.prefix == o.prefix and self.suffix == o.suffix


class WeNetUserProfilesPage:

    def __init__(self, offset: int, total: int, profiles: Optional[List[WeNetUserProfile]]):
        """
        Contains a set of profiles, used for the pagination in profiles list requests
        @param offset:
        @param total:
        @param profiles:
        """
        self.offset = offset
        self.total = total
        self.profiles = profiles

        if not isinstance(self.offset, int):
            raise TypeError("offset should be an integer")
        if not isinstance(self.total, int):
            raise TypeError("total should be an integer")
        if self.profiles:
            if isinstance(self.profiles, list):
                for profile in self.profiles:
                    if not isinstance(profile, WeNetUserProfile):
                        raise TypeError("profiles should be a list of WeNetUserProfile")
            else:
                raise TypeError("profiles should be a list of WeNetUserProfile")
        else:
            self.profiles = []

    def to_repr(self) -> dict:
        return {
            "offset": self.offset,
            "total": self.total,
            "profiles": list(x.to_repr() for x in self.profiles)
        }

    @staticmethod
    def from_repr(raw_data: dict) -> WeNetUserProfilesPage:
        profiles = raw_data.get("profiles")
        if profiles:
            profiles = list(WeNetUserProfile.from_repr(x) for x in profiles)
        return WeNetUserProfilesPage(
            offset=raw_data["offset"],
            total=raw_data["total"],
            profiles=profiles
        )

    def __eq__(self, o) -> bool:
        if not isinstance(o, WeNetUserProfilesPage):
            return False
        return self.offset == o.offset and self.total == o.total and self.profiles == o.profiles

    def __repr__(self) -> str:
        return str(self.to_repr())

    def __str__(self) -> str:
        return self.__repr__()


class UserIdentifiersPage:

    def __init__(self, offset: int, total: int, user_ids: Optional[List[str]]):
        """
        Contains a set of identifiers, used for the pagination in identifiers list requests
        @param offset:
        @param total:
        @param user_ids:
        """
        self.offset = offset
        self.total = total
        self.user_ids = user_ids

        if not isinstance(self.offset, int):
            raise TypeError("offset should be an integer")
        if not isinstance(self.total, int):
            raise TypeError("total should be an integer")
        if self.user_ids:
            if isinstance(self.user_ids, list):
                for user_id in self.user_ids:
                    if not isinstance(user_id, str):
                        raise TypeError("user_ids should be a list of str")
            else:
                raise TypeError("user_ids should be a list of str")
        else:
            self.user_ids = []

    def to_repr(self) -> dict:
        return {
            "offset": self.offset,
            "total": self.total,
            "userIds": self.user_ids
        }

    @staticmethod
    def from_repr(raw_data: dict) -> UserIdentifiersPage:
        return UserIdentifiersPage(
            offset=raw_data["offset"],
            total=raw_data["total"],
            user_ids=raw_data.get("userIds")
        )

    def __eq__(self, o) -> bool:
        if not isinstance(o, UserIdentifiersPage):
            return False
        return self.offset == o.offset and self.total == o.total and self.user_ids == o.user_ids

    def __repr__(self) -> str:
        return str(self.to_repr())

    def __str__(self) -> str:
        return self.__repr__()
