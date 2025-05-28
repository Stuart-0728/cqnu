const 主页 = { template: `<h2>欢迎来到活动报名系统</h2><p>请选择左侧导航进行操作。</p>` };
const Login = {
  template: `
    <div>
      <h2>登录</h2>
      <form @submit.prevent="doLogin">
        <div class="mb-3"><label>用户名<input v-model="username" class="form-control"></label></div>
        <div class="mb-3"><label>密码<input type="password" v-model="password" class="form-control"></label></div>
        <button class="btn btn-primary">登录</button>
      </form>
    </div>`,
  data() { return { username:'', password:'' }; },
  methods: {
    async doLogin() {
      try {
        const resp = await axios.post('/api/auth/login', { username:this.username, password:this.password });
        localStorage.setItem('token', resp.data.token);
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + resp.data.token;
        this.$router.push('/activities');
      } catch(e) { alert('登录失败'); }
    }
  }
};
const Register = {
  template: `
    <div>
      <h2>注册</h2>
      <form @submit.prevent="doRegister">
        <div class="mb-3"><label>用户名<input v-model="username" class="form-control"></label></div>
        <div class="mb-3"><label>邮箱<input v-model="email" class="form-control"></label></div>
        <div class="mb-3"><label>密码<input type="password" v-model="password" class="form-control"></label></div>
        <button class="btn btn-primary">注册</button>
      </form>
    </div>`,
  data() { return { username:'', email:'', password:'' }; },
  methods: {
    async doRegister() {
      try {
        await axios.post('/api/auth/register', { ...this.$data });
        alert('注册成功，请登录');
        this.$router.push('/login');
      } catch(e) { alert('注册失败'); }
    }
  }
};
const Activities = {
  template: `
    <div>
      <h2>活动列表</h2>
      <ul class="list-group">
        <li v-for="act in activities" :key="act.id" class="list-group-item">
          <strong>{{ act.title }}</strong> <button class="btn btn-sm btn-success float-end" @click="signUp(act.id)">报名</button>
          <p>{{ act.description }}</p>
        </li>
      </ul>
    </div>`,
  data() { return { activities: [] }; },
  async created() {
    const resp = await axios.get('/api/activity');
    this.activities = resp.data;
  },
  methods: { async signUp(id) {
      await axios.post(`/api/registration/${id}`);
      alert('报名成功');
    }}
};
const MyRegistrations = {
  template: `
    <div><h2>我的报名</h2><ul class="list-group">
      <li v-for="r in regs" :key="r.id" class="list-group-item">
        活动ID: {{ r.activity_id }} 状态: {{ r.status }} 时间: {{ r.timestamp }}
      </li>
    </ul></div>`,
  data() { return { regs: [] }; },
  async created() {
    const resp = await axios.get('/api/registration/me');
    this.regs = resp.data;
  }
};
const Profile = { template:'<h2>个人资料</h2><p>功能待完善</p>' };
const Admin = { template:'<h2>管理面板</h2><p>功能待完善</p>' };

// 路由配置
const routes = [
  { path:'/', component:主页 },
  { path:'/login', component:Login },
  { path:'/register', component:Register },
  { path:'/activities', component:Activities },
  { path:'/my-registrations', component:MyRegistrations },
  { path:'/profile', component:Profile },
  { path:'/admin', component:Admin }
];
const router = VueRouter.createRouter({ history: VueRouter.createWebHistory(), routes });

// 全局初始化
axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('token');

const app = Vue.createApp({
  data() { return { currentUser: null }; },
  async created() {
    try {
      const resp = await axios.get('/api/auth/me');
      this.currentUser = resp.data;
    } catch {};
  },
  methods: {
    logout() {
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      this.currentUser = null;
      this.$router.push('/');
    }
  }
});
app.use(router).mount('#app');
