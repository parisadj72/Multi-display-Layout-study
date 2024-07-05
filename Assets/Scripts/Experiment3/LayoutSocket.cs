using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;

public class LayoutSocket : MonoBehaviour
{
    private XRSocketInteractor socketInteractor;
    private string lastIcon;
    void Start()
    {
        socketInteractor = GetComponent<XRSocketInteractor>();
    }

    public void OnAttach()
    {
        IXRSelectInteractable obj = socketInteractor.GetOldestInteractableSelected();

        print(obj.transform.name);

        if (obj.transform.GetComponent<View>() != null)
        {
            lastIcon = obj.transform.GetComponent<View>().Icon;
            print("Icon is: " + lastIcon);
        }
    }
}
