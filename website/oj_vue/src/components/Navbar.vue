<template>
  <div class="po-navbar">
    <nav class="navbar navbar-default navbar-fixed-top">
        <div class="container-fluid">
          <div class="navbar-header">
            <a class="navbar-brand" v-link="{ path: '/' }">{{ brand_text }}</a>
          </div>
          <div class="collapse navbar-collapse">
            <ul class="nav navbar-nav navbar-left">
              <li><a v-link="{ path: '/problemlist' }">Problems</a></li>
              <li><a v-link="{ path: '/statuslist' }">Status</a></li>
              <li><a v-link="{ path: '/contestlist' }">Contests</a></li>
            </ul>
            <ul class="nav navbar-nav navbar-right">
              <template v-if="isLogin">
              <li><a id="user-id" v-link="{ path: '/user/' + current_user_id}">
                {{ current_user }}
              </a></li>
              <li><a @click="logout()">
                Logout
              </a></li>
              </template>
              <template v-else>
              <li><a @click="showLoginSidebar = true">
                Login
              </a></li>
              <li><a @click="showRegisterSidebar = true">
                Register
              </a></li>
              </template>
            </ul>
          </div>
        </div>
    </nav>

    <validator name="validation">
      <sidebar :show.sync="showLoginSidebar" placement="right" header="Login" :width="350">
        <div class="sidebar-input">
          <input class="form-control"
                 type="text"
                 v-validate:loginusername="{ required: true, username: true }"
                 placeholder="User name"
                 @keyup.enter="login(loginIsValid)"
                 id="login-user-name"
                 autofocus="autofocus">
        </div>
        <div class="sidebar-input">
          <input class="form-control"
                 type="password"
                 v-validate:loginpassword="{ required: true, password: true }"
                 placeholder="Password"
                 @keyup.enter="login(loginIsValid)"
                 id="login-password">
        </div>
        <alert
          type="danger"
          class="sidebar-alert"
          :show.sync="showLoginFailedAlert">
          <strong>Login Failed</strong>
          <p>Please check your username or password and retry!</p>
        </alert>
        <div class="sidebar-button">
          <button
                  class="btn"
                  v-bind:class="{'disabled': !loginIsValid, 'btn-success': loginIsValid}"
                  @click="login(loginIsValid)"
                  id="login-submit-button">Login</button>
        </div>
      </sidebar>

      <sidebar :show.sync="showRegisterSidebar" placement="right" header="Register" :width="350">
        <div class="sidebar-input">
          <input class="form-control"
                 type="text"
                 v-validate:registerusername="{ required: true, username: true }"
                 placeholder="User name => /^\w{4,15}$/"
                 @keyup.enter="register(registerIsValid)"
                 id="register-user-name">
        </div>
        <div class="sidebar-input">
          <input class="form-control"
                 type="email"
                 v-validate:registeremail="{ required: true, email: true}"
                 placeholder="Email => xxx@xxx.xx"
                 @keyup.enter="register(registerIsValid)"
                 id="register-email">
        </div>
        <div class="sidebar-input">
          <input class="form-control"
                 type="password"
                 v-validate:registerpassword="{ required: true, password: true }"
                 placeholder="Password => /^\S{8,16}$/"
                 @keyup.enter="register(registerIsValid)"
                 id="register-password">
        </div>
        <alert
          type="success"
          class="sidebar-alert"
          :show.sync="showRegisterSuccessAlert">
          <strong>Register Success</strong>
          <p>You successfully register to PotatoOJ.</p>
          <p>You can login your new account now!</p>
        </alert>
        <alert
          type="danger"
          class="sidebar-alert"
          :show.sync="showRegisterFailedAlert">
          <strong>Register Failed</strong>
          <p>Maybe you could change your username or email address and try again!</p>
        </alert>
        <div class="sidebar-button">
          <button
                  class="btn"
                  v-bind:class="{'disabled': !registerIsValid, 'btn-success': registerIsValid}"
                  @click="register(registerIsValid)"
                  id="register-submit-button">Sign in</button>
        </div>
      </sidebar>
    </validator>
  </div>
</template>

<script>
import { aside } from 'vue-strap'
import { alert } from 'vue-strap'
var NProgress = window.NProgress
var Cookie = window.Cookie

export default {
  name: 'navbar',
  data () {
    // Default value of datas
    return {
      brand_text: 'Potato OJ',
      current_user: null,
      current_user_id: null,
      isLogin: false,
      showLoginSidebar: false,
      showLoginFailedAlert: false,
      showRegisterSidebar: false,
      showRegisterSuccessAlert: false,
      showRegisterFailedAlert: false
    }
  },
  computed: {
    loginIsValid: function () {
      return this.$validation.loginusername.valid && this.$validation.loginpassword.valid
    },
    registerIsValid: function () {
      return this.$validation.registerusername.valid && this.$validation.registeremail.valid && this.$validation.registerpassword.valid
    }
  },
  validators: {
    email: function (val) {
      return /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(val)
    },
    username: function (val) {
      return /^\w{4,15}$/.test(val)
    },
    password: function (val) {
      return /^\S{8,16}$/.test(val)
    }
  },
  methods: {
    // ------------------------------------------------------------
    whoami: function () {
      // This funtion used to update data->current_user and isLogin
      // Run this function in ready phase
      // Run this function after login success and logout success
      // Fetch and update user infos
      let self = this
      window.fetch('/api/whoami/?format=json', {
        credentials: 'include'
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        if (data.user !== 'AnonymousUser') {
          self.current_user = data.user
          self.current_user_id = data.id
          self.isLogin = true
        } else {
          self.current_user = null
          self.isLogin = false
        }
      }).catch(function (error) {
        console.log('Error happned whoami', error)
      })
    },
    // ------------------------------------------------------------
    // ------------------------------------------------------------
    // ------------------------------------------------------------
    login: function (isValid) {
      // If this button is invalid, just return
      if (isValid === false) {
        return
      }
      // Disable button
      document.getElementById('login-submit-button').className = 'btn btn-success disabled'
      // Store this
      let self = this
      // Get username password and csrftoken value
      let username = document.getElementById('login-user-name').value
      let password = document.getElementById('login-password').value
      let csrftoken = Cookie.get('csrftoken')
      // Show progress bar
      NProgress.start()
      // Using Ajax(fetch) to login
      window.fetch('/api/login/?format=json', {
        method: 'post',
        headers: {
          'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        credentials: 'include',
        body: `username=${username}&password=${password}&csrfmiddlewaretoken=${csrftoken}`
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        // Get data success
        // Check data
        if (data.success) {
          // Login success, run whoami to update user status
          document.getElementById('login-submit-button').className = 'btn btn-success'
          self.showLoginSidebar = false
          self.showLoginFailedAlert = false
          self.whoami()
          // Reload page
          window.location.reload()
        } else {
          // Login failed, show messages
          document.getElementById('login-submit-button').className = 'btn btn-warning'
          self.showLoginFailedAlert = true
          console.log(data.detail)
        }
        NProgress.done()
      }).catch(function (error) {
        console.log('Error happend when login!', error)
        NProgress.done()
      })
    },
    // ------------------------------------------------------------
    // ------------------------------------------------------------
    // ------------------------------------------------------------
    logout: function () {
      // Check user is or not already logged in
      if (this.isLogin === false || this.current_user === null) {
        return
      }
      let self = this
      NProgress.start()
      // Fetch Logout API
      window.fetch('/api/logout/?format=json', {
        credentials: 'include'
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        // Get data success
        if (data.success) {
          // Logout success
          // Run whoami update user status
          self.whoami()
          // Reload page
          window.location.reload()
        } else {
          console.log('Logout Failed')
        }
        NProgress.done()
      }).catch(function (error) {
        NProgress.done()
        console.log('Error happned logout', error)
      })
    },
    // ------------------------------------------------------------
    // ------------------------------------------------------------
    // ------------------------------------------------------------
    register: function (isValid) {
      // If this button is invalid, just return
      if (isValid === false) {
        return
      }
      // Disable button
      document.getElementById('register-submit-button').className = 'btn btn-success disabled'
      // Store this
      let self = this
      self.showRegisterFailedAlert = false
      // Get username password and csrftoken value
      let username = document.getElementById('register-user-name').value
      let email = document.getElementById('register-email').value
      let password = document.getElementById('register-password').value
      // Show progress bar
      this.showLoginSidebar = false
      NProgress.start()
      // Using Ajax(fetch) to register
      window.fetch('/api/register/?format=json', {
        method: 'post',
        headers: {
          'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        credentials: 'include',
        body: `username=${username}&email=${email}&password=${password}`
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        // Get data success
        if (data.success) {
          // Regester success
          // auto open login sidebar
          self.showRegisterSuccessAlert = true
          setTimeout(function () {
            self.showRegisterSidebar = false
            self.showLoginSidebar = true
            self.showRegisterSuccessAlert = false
          }, 3000)
        } else {
          // Regester failed
          self.showRegisterFailedAlert = true
          document.getElementById('register-submit-button').className = 'btn btn-warning'
          console.log(data.detail)
        }
        NProgress.done()
      }).catch(function (error) {
        console.log('Error happend when Register!', error)
        document.getElementById('register-submit-button').className = 'btn btn-warning'
        NProgress.done()
      })
    }
  },
  ready: function () {
    // Update user infos
    this.whoami()
  },
  components: {
    'sidebar': aside,
    'alert': alert
  }
}
</script>

<style lang='less'>

// navbar colors
@nav-backgroud-color: #FFFFFF;
@nav-brand-color: #E75440;
@nav-font-color: #000000;
@nav-base-color: #FFFFFF;
@nav-hover-color: green;
@sidebar-title-color: white;

// hover border width, just modify here, don't modify other place
@nav-border-width: 3px;

.po-navbar {
  nav {
    background-color: @nav-backgroud-color;
    margin-bottom: 0px;
    z-index: 1;
  }

  .navbar-default .navbar-brand {
    font-family: 'Audiowide', cursive;
    color: @nav-brand-color;
    font-size: 20px;
  }

  .navbar-right {
    margin-right: 0px;
    padding-right: 28px;
    li a{
      padding-left: 0px;
      &:hover {
        cursor:pointer
      }
    }
  }

  .navbar-collapse .navbar-left li a {
    font-family: 'Exo 2', sans-serif;
    font-weight: 400;

    border-bottom-color: @nav-base-color;
    border-bottom-width: @nav-border-width;
    border-bottom-style: solid;
    padding-bottom: 15px - @nav-border-width;      
    color: @nav-font-color;

    &:hover {
      border-bottom-color: @nav-hover-color;
      color: @nav-font-color;
    }
  }

  // change active link's color
  .navbar-collapse .navbar-left .v-link-active{
      border-bottom-color: @nav-hover-color;
  }

  .aside .aside-dialog .aside-header {
    color: black;
    background-color: @sidebar-title-color;
    .close {
      font-family: sans-serif;
      color: black;
    }
  }

  .sidebar-input {
    padding-top:20px;
    .form-control {
      border-radius: 0px;
    }
  }

  .sidebar-button {
    padding-top: 20px;
    float: right;

    .btn {
      border-radius: 2px;
    }
  }

  .sidebar-alert {
    margin-top: 20px;
    margin-bottom: 0px;
  }
}

</style>
