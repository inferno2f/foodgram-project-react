import shutil
import tempfile
from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import (APIClient, APIRequestFactory, APITestCase,
                                 force_authenticate)

from users.models import CustomUser

from .models import Ingredient, Recipe, Tag
from .views import RecipeViewSet

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


class FoodgramViewsTests(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        small_image = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.jpeg", content=small_image, content_type="image/jpeg"
        )
        cls.user = CustomUser.objects.create(username="John")
        cls.ingredient = Ingredient.objects.create(
            name="test_ingredient", measurement_unit="test_unit")
        cls.tag = Tag.objects.create(
            name="test_tag", color="#000000", slug="test_tag")
        cls.recipe = Recipe.objects.create(
            name="test_recipe",
            description="test_description",
            image=uploaded,
            cooking_time=10,
            author=cls.user,
            # FIXME: разобраться как добавить тэги и ингредиенты
            # ingredients=[id=cls.ingredient.id, ],
            # tags=[1]
        )
        # cls.recipe.tags.add(cls.tag)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = CustomUser.objects.get(username=self.user.username)

    def test_recipes_page(self):
        """ Test recipes page for unauthorized user """
        request = self.client.get("/api/recipes/")
        self.assertEqual(
            request.status_code, HTTPStatus.OK,
            "Unauthorized user can't see recipes page")

    def test_user_signup(self):
        """ Test user signup """
        request = self.client.post(
            "/api/users/",
            {
                "username": "guest_user",
                "email": "test@test.com",
                "password": "bad_password",
                "first_name": "test_first_name",
                "last_name": "test_last_name",
            },
            format="json"
        )
        self.assertEqual(request.status_code, HTTPStatus.CREATED)
        self.assertTrue(CustomUser.objects.filter(
            username="guest_user").exists(), "User was not found in DB")

    def test_unauthorized_user_post_recipe(self):
        """ Test unauthorized user can't post recipe """
        request = self.client.post(
            "/api/recipes/",
            {
                "name": "unauthorized_user_recipe",
                "description": "test_description",
                "image": "test_image",
                "cooking_time": 10,
            },
            format="json"
        )
        self.assertEqual(request.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertFalse(Recipe.objects.filter(
            name="unauthorized_user_recipe").exists(), "Recipe was created")

    def test_fetch_recipe_detail(self):
        """ Test fetching recipe detail """
        request = self.client.get(
            f"/api/recipes/{self.recipe.id}/",
            format="json"
        )
        self.assertEqual(request.status_code, HTTPStatus.OK)
        self.assertEqual(
            request.data["name"], self.recipe.name,
            "Recipe name is not equal to expected")
        self.assertEqual(
            request.data["description"], self.recipe.description,
            "Recipe description is not equal to expected")
        self.assertEqual(
            request.data["cooking_time"], self.recipe.cooking_time,
            "Recipe cooking time is not equal to expected")
        self.assertEqual(
            request.data["author"]["username"], self.recipe.author.username,
            "Recipe author is not equal to expected")
        # self.assertEqual(
        #     request.data["tags"], self.tag,
        #     "Recipe tag is not equal to expected")
        # self.assertEqual(
        #     request.data["ingredients"][0]["name"],
        #     self.recipe.ingredients.first().name,
        #     "Recipe ingredient is not equal to expected")

    def test_update_recipe(self):
        """ Test updating recipe """
        view = RecipeViewSet.as_view({"put": "update"})
        request = self.factory.put(
            f"/api/recipes/{self.recipe.id}/",
            {
                "name": "test_recipe_update",
                "description": "test_description_update",
                "cooking_time": 20,
                "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVQYV2NgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII=",
                "tags": [1],
                "ingredients": [{"ingredient": self.ingredient.id, "amount": 1, "recipe": self.recipe.id}],
            },
            format="json"
        )
        force_authenticate(user=self.user, request=request)
        response = view(request, pk=self.recipe.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.data, "test_recipe_update",
            "Recipe name is not equal to expected")
        self.assertEqual(
            response.data["description"], "test_description_update",
            "Recipe description is not equal to expected")
        self.assertEqual(
            response.data["cooking_time"], 20,
            "Recipe cooking time is not equal to expected")
        self.assertEqual(
            request.data["author"]["username"], self.user.username,
            "Recipe author is not equal to expected")
        # self.assertEqual(
        #     request.data["tags"][0]["name"], "test_tag",
        #     "Recipe tag is not equal to expected")
        # self.assertEqual(
        #     request.data["ingredients"][0]["name"],
        #     self.ingredient.name,
        #     "Recipe ingredient is not equal to expected")
