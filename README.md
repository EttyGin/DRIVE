NCCL share/68eeae5c-7bfc-8011-b924-296b8cd47b1c

smart log/68ec3ab3-daf8-8011-8f15-838ff8631941

https://github.com/surajssd/llm-k8s/blob/8a7fbb969b1edaa8ab40ee9c35dc3bba62c1a6d6/deepseek-v2.5/02_tp8_pp2_ib/lws.sh#L291-L294
https://docs.vllm.ai/en/v0.8.5/serving/distributed_serving.html
https://docs.vllm.ai/en/v0.8.5/getting_started/troubleshooting.html#troubleshooting-incorrect-hardware-driver
=============


gooddddddd https://chatgpt.com/share/694870e2-ba8c-8011-8eb7-c4dd7ffea90d
https://chatgpt.com/share/691253c9-c838-8011-9e78-fdcb3ce4a4df
https://chatgpt.com/share/6912564a-8f20-8011-b17b-e9c8bd7f6ac4
<img width="219" height="219" alt="image" src="https://github.com/user-attachments/assets/c56a202d-570a-4af6-9773-6d79751ebe5c" />


[https://chatgpt.com/c/6941b1c5-5d00-8327-b106-29e4d46e3a25
](https://chatgpt.com/share/69432058-35f4-8011-86fe-d8a75e262778)

-------------------
    <div class="image-container" style="text-align: center; margin: 40px 0; padding: 0;">
      <img src="https://top-selfie.co.il/wp-content/uploads/2021/05/sunset-1373171.jpg" alt="Sunset"
        style="width: 200px; height: auto; display: inline-block;" />
    </div>
-------------------
hub:
  extraConfig:
    addTemplatePath: |
      import os
      c.JupyterHub.template_paths = c.JupyterHub.template_paths or []
      c.JupyterHub.template_paths.insert(0, "/usr/local/share/jupyterhub/custom_templates")
  
  extraFiles:
    # footer
    footer.html:
      mountPath: /usr/local/share/jupyterhub/custom_templates/footer.html
      stringData: |
          <div style="position:fixed; bottom:0; left:0; right:0; background:#f37524; color:white; text-align:center; padding:15px; z-index:999999;">
              <a href="https://he.wikipedia.org" target="_blank" style="color:white;">Documentation</a> |
              <a href="https://he.wikipedia.org" target="_blank" style="color:white;">Common Issues</a>
          </div>
    
    # page.html - התבנית הבסיסית
    page.html:
      mountPath: /usr/local/share/jupyterhub/custom_templates/page.html
      stringData: |
          {% extends "templates/page.html" %}
          {% block footer %}
              {% include "footer.html" %}
          {% endblock %}
    
    # login.html - עם לוגו מ-GitHub מתחת לחלונית ההרשמה
    login.html:
      mountPath: /usr/local/share/jupyterhub/custom_templates/login.html
      stringData: |
          {% extends "templates/login.html" %}
          
          {% block login %}
          {{ super() }}
          
          <!-- לוגו מותאם אישית מתחת לחלונית ההרשמה -->
          <div style="text-align: center; margin-top: 30px; margin-bottom: 80px;">
              <img src="https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/logo.png" 
                   alt="Company Logo" 
                   style="max-width: 300px; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
              <p style="margin-top: 15px; color: #666; font-size: 16px; font-weight: 500;">
                  ברוכים הבאים למערכת שלנו
              </p>
          </div>
          {% endblock %}
          
          {% block footer %}
              {% include "footer.html" %}
          {% endblock %}
