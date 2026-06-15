# API and Routing Documentation

## 1. Core Endpoints
These are the main landing pages and discovery hubs of the application.

| URL Path | Route Name | View | Description |
| :--- | :--- | :--- | :--- |
| `/` | `home` | `HomeView` | The main landing page/dashboard of the application. |
| `/discover/` | `discover` | `DiscoverView` | A feed or hub for exploring new content, featured speedruns, or games. |

---

## 2. User Authentication & Profiles
Handles user lifecycle operations including authentication, profile management, and user discovery.

### **Authentication**
* **POST/GET** `/user/login` (`user-login`) → `LoginView`
    * Renders the login form and processes user authentication.
* **POST/GET** `/user/register` (`user-register`) → `RegisterView`
    * Handles new user account registration.
* **POST** `/user/logout` (`user-logout`) → `LogoutView`
    * Logs out the current user and clears the session.

### **Profile Management & Discovery**
* **GET** `/user/<str:username>/` (`user-profile`) → `UserProfileView`
    * Displays the public profile of a specific user based on their unique username.
* **POST/GET** `/user/<str:username>/edit/` (`edit-profile`) → `EditUserProfileView`
    * Allows users to update their profile information. (Requires authorization).
* **POST/DELETE** `/user/delete` (`delete-profile`) → `DeleteUserView`
    * Permanently deletes the authenticated user's account.
* **GET** `/users/search/` (`user-search`) → `SearchUserView`
    * Handles queries to find specific users via search parameters.

---

## 3. Account & Email Verification
Manages security-related flows, password resets, and email modifications.

### **Email Activation & Account Creation**
* **GET** `/verify-email/<str:uidb64>/<str:token>/` (`verify-email`) → `EmailVerificationView`
    * Validates the user's email activation link using an encoded user ID (`uidb64`) and a secure token.
* **POST/GET** `/resend-verification/` (`resend-verification`) → `ResendVerificationEmailView`
    * Triggers a new verification email to be sent to the user.
* **GET** `/verify-pending/` (`verification-pending`) → `verificationPendingView`
    * Renders an intermediary notice page informing the user that they need to verify their email before continuing.

### **Credentials & Security Changes**
* **POST/GET** `/reset-password/<str:token>/` (`reset-password`) → `ResetPasswordView`
    * Allows users to set a new password via a secure token received in their email.
* **GET** `/change-email/<str:uidb64>/<str:token>/` (`change-email`) → `ChangeEmailView`
    * Verifies and processes a user's request to update their primary email address.

---

## 4. Games & Leaderboards
Allows navigation through the catalog of supported games and their respective categories.

* **GET** `/games/` (`game-list`) → `GamesView`
    * Lists all games available in the system for speedrunning.
* **GET** `/games/<int:game_id>/` (`game-detail`) → `GameDetailView`
    * Displays specific details about a game (e.g., description, rules, and links to its sub-categories).
* **GET** `/games/<int:game_id>/speedrun-types/<int:type_id>/` (`category-leaderboard`) → `CategoryLeaderboardView`
    * Displays the ranked leaderboard for a specific category or "speedrun type" (e.g., Any%, 100%) belonging to a specific game.

---

## 5. Speedruns (Submissions & Management)
Handles CRUD operations for individual run submissions within specific game categories.

* **GET** `/games/<int:game_id>/speedrun-types/<int:type_id>/speedruns/<int:speedrun_id>/` (`speedrun-view`) → `SpeedrunDetailView`
    * Displays detailed information, video links, notes, and stats for a specific speedrun submission.
* **POST/GET** `/games/<int:game_id>/speedrun-types/<int:type_id>/speedruns/` (`speedrun-upload`) → `SpeedrunUploadView`
    * Handles the submission/upload form and processing for a new speedrun run under a specific category.
* **POST/DELETE** `/games/<int:game_id>/speedrun-types/<int:type_id>/speedruns/<int:speedrun_id>/delete/` (`speedrun-delete`) → `SpeedrunDeleteView`
    * Deletes a specific speedrun submission (typically restricted to the runner or site moderators).

---

## 6. Requests & Reporting
Moderation and administrative pipelines for community management.

* **POST/GET** `/requests/submit/` (`request-submit`) → `RequestSubmissionView`
    * Allows users to submit community requests (e.g., requesting a new game or category to be added to the site).
* **POST/GET** `/user/<str:username>/report/` (`report-user`) → `ReportUserView`
    * Allows users to file a report against a specific user profile for rule violations.
* **POST/GET** `/speedruns/<int:speedrun_id>/report/` (`report-speedrun`) → `ReportSpeedrunView`
    * Allows users to flag/report a suspicious or illegitimate speedrun run for moderator review.

---

## 7. System & Error Handling
Explicit routing overrides for error presentation.

* **GET** `/404/` (`page-not-found`) → `PageNotFoundView`
    * Explicitly renders the custom 404 Error page layout.

---

# Public API Endpoints (REST)

These endpoints are powered by Django REST Framework `ReadOnlyModelViewSet` classes, providing public, read-only (GET) access to the core database models.


---

## 1. Games API
Public endpoints to view the catalog of registered games and their associated categories.

| Method | URL Path | ViewSet | Description |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/games/` | `PublicGameViewSet` | **List View:** Returns a list of all registered games in the system. |
| **GET** | `/api/games/<int:id>/` | `PublicGameViewSet` | **Detail View:** Returns the complete details of a specific game using its ID. |

---

## 2. Speedruns API
Public endpoints to explore verified speedrun submissions. 

| Method | URL Path | ViewSet | Description |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/speedruns/` | `PublicSpeedrunViewSet` | **List View:** Returns a feed of all accepted speedrun submissions. |
| **GET** | `/api/speedruns/<int:id>/` | `PublicSpeedrunViewSet` | **Detail View:** Returns the complete details of a specific accepted speedrun using its ID. |
